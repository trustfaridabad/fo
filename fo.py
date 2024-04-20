import pandas as pd
import numpy as np
from datetime import timedelta
from datetime import datetime
import yfinance as yf
import time
import pandas_ta as ta
from dateutil.relativedelta import relativedelta
import datetime as dt
import warnings
warnings.filterwarnings('ignore')
import streamlit as st


# Add a horizontal rule and then display the centered title

#st.markdown("<h1 style='text-align: left;'>Daily Stock Data Analysis</h1>", unsafe_allow_html=True)
# Set page configuration
st.set_page_config(
    page_title="Daily Stock Data Analysis",
    page_icon=":rocket:",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("---")

if st.sidebar.button("Clear Cache"):
    # Clear cache data
    st.cache_data.clear()
    st.cache_resource.clear()

# import nifty 500 stocks

tickers = pd.read_csv("fo_symbol.csv") +".NS"

#st.write(tickers)

# Get List of NSE 500
tickers = tickers['SYMBOL'].values

# define interval
begin_time = datetime.today()-timedelta(days=90)
end_time = datetime.today()

# # download the historical data
@st.cache_data
def get(tickers, startdate, enddate):
    @st.cache_resource
    def data(tickers):
        return (yf.download(tickers, start=startdate, end=enddate))
    datas = map(data, tickers)
    return(pd.concat(datas, keys=tickers, names=['Ticker', 'Date']))

all_data = get(tickers, begin_time, end_time)

# get the only closing price
df = np.round(all_data[['Adj Close','Volume','Open','High','Low']].reset_index(),2) 
df.rename(columns={'Adj Close':'Close'}, inplace=True)

# Group by ticker
grouped_data = df.groupby('Ticker')

# Define a function to apply technical analysis
@st.cache_data
def apply_ta(group_df):
    group_df['Prev_Close'] = group_df['Close'].shift(1)
    group_df['Ch%'] = (group_df['Close']-group_df['Prev_Close'])/group_df['Prev_Close']*100

    group_df['RSI'] = group_df.ta.rsi(length=22, append=True).round(2)
    group_df['Supertrend'] = group_df.ta.supertrend(period=13, multiplier=4, append=True)['SUPERT_7_4.0'].round(2)
    group_df['Call'] = np.where(group_df['Close'] > group_df['Supertrend'], "Buy", "Sell")
    return group_df

# Apply technical analysis using apply function
df_with_ta = grouped_data.apply(apply_ta).reset_index(drop=True)
df_with_ta = df_with_ta[['Date','Ticker','Close', 'Volume', 'Ch%', 'RSI', 'Supertrend','Call']]
data = df_with_ta.drop_duplicates(subset=['Ticker'], keep='last')
data['Date'] = pd.to_datetime(data['Date']).dt.date
RSI = st.sidebar.slider('Select RSI input', 20, 100, 40)

data = data[data['RSI'] < RSI]
st.dataframe(data, hide_index=True)
st.sidebar.info("Designed by Shiv")

