import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import alpaca_trade_api as tradeapi
from pytz import timezone
import requests

# Streamlit app title
st.title("Moving Average Cross Detection - S&P 500 & NASDAQ by GeekendZone!")

# Sidebar for API keys
with st.sidebar:
    st.header("Alpaca API Configuration")
    api_key = st.text_input("API Key", value="PK3O2J7KSHRME7LI95AB", type="password")
    api_secret = st.text_input("API Secret", value="gjXeodXRbJZ9LT3gqSPRHMfFsjCBaTSS7lXE1hws", type="password")
    base_url = st.selectbox(
        "API URL",
        ["https://paper-api.alpaca.markets", "https://api.alpaca.markets"],
        index=0  # Default to paper trading
    )

    # Index selection
    st.header("Index Selection")
    index_choice = st.radio(
        "Select Index to Analyze",
        ["S&P 500", "NASDAQ", "Both"],
        index=2  # Default to both
    )
    
    # Add timeframe parameters
    st.header("Parameters")
    timeframe = st.selectbox(
        "Select Timeframe",
        ["5Min", "15Min", "1Hour", "4Hour", "1Day"],
        index=4  # Default to daily
    )
    
    ma_type = st.selectbox(
        "Moving Average Type",
        ["SMA", "EMA"],
        index=0  # Default to SMA
    )
    
    # Fast and Slow MA periods
    FAST = st.number_input("Fast MA Period", min_value=1, value=50, step=1)
    SLOW = st.number_input("Slow MA Period", min_value=1, value=200, step=1)
    
    # Window for recent crosses
    WINDOW_D = st.slider("Recent Cross Window (Days)", min_value=1, max_value=30, value=7)
    
    # Number of results to show
    MAX_RESULTS = st.number_input("Max Results to Show", min_value=5, value=45, step=5)

# Function to get S&P 500 symbols
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_sp500_symbols():
    try:
        table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
        return table['Symbol'].str.replace(".", "-").tolist()  # Replace dots with dashes for Alpaca compatibility
    except Exception as e:
        st.error(f"Error fetching S&P 500 symbols: {e}")
        return []

# Function to get NASDAQ symbols (top 100)
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_nasdaq_symbols():
    try:
        table = pd.read_html('https://en.wikipedia.org/wiki/Nasdaq-100')[1]
        return table['Ticker'].str.replace(".", "-").tolist()  # Replace dots with dashes for Alpaca compatibility
    except Exception as e:
        st.error(f"Error fetching NASDAQ symbols: {e}")
        return []

# Initialize Alpaca API if credentials are provided
if api_key and api_secret:
    try:
        api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
        
        # Get symbols based on selection
        symbols = []
        if index_choice in ["S&P 500", "Both"]:
            sp500 = get_sp500_symbols()
            symbols.extend(sp500)
            st.write(f"S&P 500 companies: {len(sp500)}")
            
        if index_choice in ["NASDAQ", "Both"]:
            nasdaq = get_nasdaq_symbols()
            symbols.extend(nasdaq)
            st.write(f"NASDAQ companies: {len(nasdaq)}")
        
        # Remove duplicates
        symbols = list(set(symbols))
        st.write(f"Total unique symbols to analyze: {len(symbols)}")
        
        # Map of timeframe to lookback period (to ensure enough data for calculations)
        lookback_map = {
            "5Min": 30,     # 30 days for 5-minute data
            "15Min": 60,    # 60 days for 15-minute data
            "1Hour": 90,    # 90 days for hourly data
            "4Hour": 180,   # 180 days for 4-hour data
            "1Day": 500,    # 500 days for daily data (to accommodate 200-day MA)
        }
        
        # Calculate dates
        end_date = datetime.now(timezone('US/Eastern'))
        start_date = end_date - timedelta(days=lookback_map[timeframe])
        
        # Progress bar for data loading
        progress_bar = st.progress(0)
        
        # Function to get data for a symbol
        @st.cache_data(ttl=3600)  # Cache for 1 hour
        def get_stock_data(symbol, timeframe, start, end):
            try:
                bars = api.get_bars(
                    symbol, 
                    timeframe,
                    start=start.isoformat(), 
                    end=end.isoformat(),
                    adjustment='raw'
                ).df
                return bars['close'] if not bars.empty else None
            except Exception as e:
                return None
        
        # Collect data for all symbols
        all_data = {}
        total_symbols = len(symbols)
        
        st.text(f"Loading data for {total_symbols} symbols...")
        
        for i, symbol in enumerate(symbols):
            progress_bar.progress((i + 1) / total_symbols)
            prices = get_stock_data(symbol, timeframe, start_date, end_date)
            if prices is not None and len(prices) > SLOW:  # Ensure enough data points
                all_data[symbol] = prices
        
        # Create DataFrame from all data
        prices_df = pd.DataFrame(all_data)
        
        if not prices_df.empty:
            st.success(f"Successfully loaded data for {len(prices_df.columns)} symbols")
            
            # Calculate moving averages based on type
            if ma_type == "SMA":
                fast = prices_df.rolling(FAST).mean()
                slow = prices_df.rolling(SLOW).mean()
            else:  # EMA
                fast = prices_df.ewm(span=FAST, adjust=False).mean()
                slow = prices_df.ewm(span=SLOW, adjust=False).mean()
            
            # Identify crossovers
            cross = (fast.shift(1) < slow.shift(1)) & (fast >= slow)
            
            # Find the last crossover for each symbol
            last = pd.Series(index=cross.columns, dtype='datetime64[ns]')
            for col in cross.columns:
                if cross[col].any():
                    cross_dates = cross[col][cross[col]].index
                    if len(cross_dates) > 0:
                        last[col] = cross_dates[-1]
                    else:
                        last[col] = pd.NaT
                else:
                    last[col] = pd.NaT
            
            # Determine recent crossovers
            if timeframe == "1Day":
                cutoff = prices_df.index.max() - timedelta(days=WINDOW_D)
            else:
                # For intraday, convert WINDOW_D to the appropriate number of bars
                bars_per_day = {
                    "5Min": 78,  # ~6.5 trading hours * 12 5-min bars per hour
                    "15Min": 26,  # ~6.5 trading hours * 4 15-min bars per hour
                    "1Hour": 7,   # ~6.5 trading hours per day
                    "4Hour": 2,   # ~2 4-hour bars per day
                }
                window_bars = WINDOW_D * bars_per_day.get(timeframe, 1)
                cutoff = prices_df.index.max() - pd.Timedelta(minutes=window_bars * 
                                                     int(timeframe.replace('Min', '').replace('Hour', '')) * 
                                                     (1 if 'Min' in timeframe else 60))
            
            recent = last >= cutoff
            
            # Get index membership for each symbol
            index_membership = {}
            sp500_set = set(get_sp500_symbols()) if index_choice in ["S&P 500", "Both"] else set()
            nasdaq_set = set(get_nasdaq_symbols()) if index_choice in ["NASDAQ", "Both"] else set()
            
            for symbol in last.index:
                indices = []
                if symbol in sp500_set:
                    indices.append("S&P 500")
                if symbol in nasdaq_set:
                    indices.append("NASDAQ")
                index_membership[symbol] = ", ".join(indices)
            
            # Create summary DataFrame
            summary = pd.DataFrame({
                "Symbol": last.index,
                "Index": [index_membership.get(symbol, "") for symbol in last.index],
                "Last Cross": last,
                "Fast MA": FAST,
                "Slow MA": SLOW,
                "MA Type": ma_type,
                "Recent?": ["✅" if r else "" for r in recent]
            })
            
            # Format date for display
            summary["Last Cross"] = summary["Last Cross"].dt.strftime('%Y-%m-%d %H:%M')
            
            # Sort and display results
            summary = summary.sort_values("Last Cross", ascending=False, na_position="last")
            
            # Remove rows with NaT
            summary = summary.dropna(subset=["Last Cross"])
            
            # Display results
            st.subheader(f"Moving Average Crossover Results ({timeframe}, {ma_type})")
            st.dataframe(summary.head(MAX_RESULTS))
            
            # Show statistics
            st.subheader("Statistics")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Symbols Analyzed", len(prices_df.columns))
            col2.metric("Total Crossovers Found", len(summary))
            col3.metric("Recent Crossovers", sum(recent))
            
            # Filter for recent crosses only
            if sum(recent) > 0:
                st.subheader("Recent Crossovers Only")
                st.dataframe(summary[summary["Recent?"] == "✅"])
            
        else:
            st.error("No data available for the selected timeframe.")
            
    except Exception as e:
        st.error(f"Error connecting to Alpaca API: {str(e)}")
else:
    st.warning("Please enter your Alpaca API credentials in the sidebar to proceed.")
    
    # Show sample interface with demo data
    st.subheader("Sample Interface (Enter API keys to see actual data)")
    sample_data = pd.DataFrame({
        "Symbol": ["AAPL", "MSFT", "AMZN", "GOOGL", "TSLA"],
        "Index": ["S&P 500, NASDAQ", "S&P 500, NASDAQ", "S&P 500, NASDAQ", "S&P 500, NASDAQ", "S&P 500, NASDAQ"],
        "Last Cross": ["2023-04-15", "2023-04-10", "2023-04-05", "2023-04-01", "2023-03-28"],
        "Fast MA": [FAST] * 5,
        "Slow MA": [SLOW] * 5,
        "MA Type": [ma_type] * 5,
        "Recent?": ["✅", "✅", "", "", ""]
    })
    st.dataframe(sample_data)
