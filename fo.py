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

if st.button("Clear Cache"):
    # Clear cache data
    st.cache_data.clear()
    st.cache_resource.clear()

# import nifty 500 stocks

tickers = pd.read_csv("fo_symbol.csv") +".NS"

#st.write(tickers)

# Get List of NSE 500
tickers = tickers['SYMBOL'].values
additional_symbols = ['^NSEBANK','^NSEI']
tickers = np.append(tickers, additional_symbols)

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
    group_df['Signal'] = np.where(group_df['Close'] > group_df['Supertrend'], "Buy", "Sell")
    return group_df

# Apply technical analysis using apply function
df_with_ta = grouped_data.apply(apply_ta).reset_index(drop=True)
df_with_ta = df_with_ta[['Date','Ticker','Close', 'Volume', 'Ch%', 'RSI', 'Supertrend','Signal']]
data = df_with_ta.drop_duplicates(subset=['Ticker'], keep='last')
data['Date'] = pd.to_datetime(data['Date']).dt.date
#RSI = st.sidebar.slider('Select RSI input', 0, 100, 40)
# Define the minimum and maximum values for the range
min_value = st.sidebar.slider("Select minimum value:", min_value=0.0, max_value=100.0, value=30.0)
max_value = st.sidebar.slider("Select maximum value:", min_value=min_value, max_value=100.0, value=75.0)

data = data[(data['RSI'] < max_value) & (data['RSI'] > min_value)]
# Display table
#filter_col = st.sidebar.selectbox("Filter by", df.columns)
filter_text = st.sidebar.selectbox("Filter text", tickers)

# Filter the DataFrame

if filter_text:
    filtered_df = data[data['Symbol'].str.contains(filter_text, case=False)]
    st.dataframe(filtered_df,  hide_index = True)
else:
    st.dataframe(data,  hide_index = True)
    
#filtered_df = data[data['Ticker'].str.contains(filter_text, case=False)]
#st.dataframe(filtered_df, hide_index = True)

#st.table(data)
st.sidebar.info("Designed by Shiv")

