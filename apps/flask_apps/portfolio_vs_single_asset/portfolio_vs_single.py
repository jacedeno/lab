import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from typing import List, Dict, Union

# Configuration
APP_TITLE = "Stocks Portfolio vs Single Asset Comparison"
FAVICON_PATH = "favicon.ico"  # You'll need a favicon.ico file for this
DEFAULT_START_DATE = datetime(2015, 1, 1)
DEFAULT_END_DATE = datetime(2025, 2, 1)
DEFAULT_INITIAL_INVESTMENT = 500
DEFAULT_CONTRIBUTION = 400
DEFAULT_TICKERS = "AAPL, NVDA, MSFT, AMZN, META, GOOGL, TSLA, BRK-B, JPM"
DEFAULT_INDEX_TICKER = "SPY"

import time

@st.cache_data
def validate_ticker(ticker: str) -> bool:
    """Validates if a ticker symbol exists."""
    try:
        ticker_obj = yf.Ticker(ticker)
        info = ticker_obj.info
        return 'regularMarketPrice' in info and info['regularMarketPrice'] is not None
    except Exception as e:
        error_text = st.empty()
        error_text.error(f"Error validating ticker {ticker}: {str(e)}")
        time.sleep(1)
        error_text.empty()
        return False

@st.cache_data
def download_data(tickers: Union[str, List[str]], start: datetime, end: datetime, interval: str, max_retries: int = 3) -> pd.DataFrame:
    """Downloads stock data from Yahoo Finance with retry logic."""
    for attempt in range(max_retries):
        try:
            # If it's a list of tickers, validate each one
            if isinstance(tickers, list):
                valid_tickers = []
                for ticker in tickers:
                    if validate_ticker(ticker.strip()):
                        valid_tickers.append(ticker.strip())
                    else:
                        warning_text = st.empty()
                        warning_text.warning(f"Invalid ticker: {ticker}. Skipping...")
                        time.sleep(1)
                        warning_text.empty()
                
                if not valid_tickers:
                    st.error("No valid tickers provided.")
                    return pd.DataFrame()
                
                tickers = valid_tickers
            else:
                # Single ticker validation
                if not validate_ticker(tickers):
                    st.error(f"Invalid ticker: {tickers}")
                    return pd.DataFrame()

            # Add progress message using the parent container's empty element
            progress_msg = st.empty()
            progress_msg.text(f"Download attempt {attempt + 1}/{max_retries}...")
            
            data = yf.download(tickers, start=start, end=end, interval=interval, auto_adjust=True, progress=False)
            progress_msg.empty()
        
            if data.empty:
                warning_text = st.empty()
                warning_text.warning(f"Attempt {attempt + 1}: No data available for the specified date range.")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retrying
                    warning_text.empty()
                    continue
                st.error("Failed to get data after all attempts.")
                return pd.DataFrame()
                
            if 'Close' not in data.columns and not isinstance(data['Close'], pd.DataFrame):
                warning_text = st.empty()
                warning_text.warning(f"Attempt {attempt + 1}: Unexpected data format received.")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retrying
                    warning_text.empty()
                    continue
                st.error("Failed to get proper data format after all attempts.")
                return pd.DataFrame()
                
            return data['Close']
            
        except Exception as e:
            warning_text = st.empty()
            if attempt < max_retries - 1:
                warning_text.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2)  # Wait before retrying
                warning_text.empty()
                continue
            st.error(f"Error downloading data after {max_retries} attempts: {str(e)}")
            return pd.DataFrame()
            
    return pd.DataFrame()  # Return empty DataFrame if all attempts fail

def simulate_portfolio(stock_prices: pd.DataFrame, contribution: float, initial_investment: float) -> pd.DataFrame:
    """Simulates portfolio growth over time for a multi-stock portfolio."""
    periods = stock_prices.index
    num_tickers = len(stock_prices.columns)
    # The contribution per period is split equally among stocks.
    period_contribution = contribution / num_tickers
    shares_bought: Dict[str, np.ndarray] = {ticker: np.zeros(len(stock_prices)) for ticker in stock_prices.columns}
    leftover_cash: Dict[str, float] = {ticker: 0.0 for ticker in stock_prices.columns}
    initial_per_stock = initial_investment / num_tickers

    # Track total invested amount
    total_invested = initial_investment
    total_invested_list = [total_invested]

    # At the first period, buy as many whole shares as possible.
    portfolio_value_initial = 0.0
    for ticker in stock_prices.columns:
        price = stock_prices[ticker].iloc[0]
        initial_shares = initial_per_stock // price
        leftover_cash[ticker] = initial_per_stock % price
        shares_bought[ticker][0] = initial_shares
        portfolio_value_initial += shares_bought[ticker][0] * price

    portfolio_values = [portfolio_value_initial]
    
    for i in range(1, len(periods)):
        portfolio_value = 0.0
        total_invested += contribution
        total_invested_list.append(total_invested)
        
        for ticker in stock_prices.columns:
            price = stock_prices[ticker].iloc[i]
            total_money = period_contribution + leftover_cash[ticker]
            shares_to_buy = total_money // price
            leftover_cash[ticker] = total_money % price
            shares_bought[ticker][i] = shares_bought[ticker][i - 1] + shares_to_buy
            portfolio_value += shares_bought[ticker][i] * price
        portfolio_values.append(portfolio_value)
    return pd.DataFrame({
        'Portfolio Value': portfolio_values,
        'Total Invested': total_invested_list
    }, index=periods)

def simulate_index_investment(index_prices: pd.Series, contribution: float, initial_investment: float) -> pd.DataFrame:
    """Simulates index investment growth over time."""
    periods = index_prices.index
    shares_bought = np.zeros(len(index_prices))
    leftover_cash = 0.0

    # Track total invested amount
    total_invested = initial_investment
    total_invested_list = [total_invested]

    # Initial purchase
    price_initial = index_prices.iloc[0]
    initial_shares = initial_investment // price_initial
    leftover_cash = initial_investment % price_initial
    shares_bought[0] = initial_shares
    
    # Calculate initial portfolio value
    portfolio_values = [shares_bought[0] * price_initial]
    
    for i in range(1, len(periods)):
        price = index_prices.iloc[i]
        total_money = contribution + leftover_cash
        shares_to_buy = total_money // price
        leftover_cash = total_money % price
        shares_bought[i] = shares_bought[i - 1] + shares_to_buy
        total_invested += contribution
        total_invested_list.append(total_invested)
        portfolio_values.append(shares_bought[i] * price)
    return pd.DataFrame({
        'Index Value': portfolio_values,
        'Total Invested': total_invested_list,
        'Shares Held': shares_bought
    }, index=periods)

# Streamlit App Configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="assets/favicon.ico",
    layout="wide"
)

# Display logo and title
col1, col2 = st.columns([4, 1])
with col1:
    st.header(APP_TITLE, divider="gray")
with col2:
    st.image("assets/logo.png", width=240)
st.markdown(
    """
    This tool compares the historical performance of a custom Portfolio of stocks against a single asset (e.g., a stock, ETF, or index fund). 
    It simulates investing a fixed contribution per period (weekly, monthly, or annually) and shows how the portfolio value evolves over time.
    Remember, past performance is not indicative of future results, and this tool should not be considered financial advice.
    """
)

# Sidebar Inputs
st.sidebar.header("Input Parameters")
ticker_list = st.sidebar.text_input("Enter the ticker symbols (separated by comma)", DEFAULT_TICKERS)
tickers = [x.strip() for x in ticker_list.split(',')]
index_ticker = st.sidebar.text_input("Enter single ticker (e.g., SPY, QQQ)", DEFAULT_INDEX_TICKER)
start_date = st.sidebar.date_input("Start Date", value=DEFAULT_START_DATE)
end_date = st.sidebar.date_input("End Date", value=DEFAULT_END_DATE)
initial_amount = st.sidebar.number_input("Initial Investment (in USD)", value=DEFAULT_INITIAL_INVESTMENT, step=100)
contribution = st.sidebar.number_input("Contribution per Period (in USD)", value=DEFAULT_CONTRIBUTION, step=100)

# Options available: Weekly, Monthly only.
contrib_freq = st.sidebar.selectbox("Contribution Frequency", ["Weekly", "Monthly"])

# Set the data interval automatically based on contribution frequency.
if contrib_freq == "Weekly":
    interval = "1wk"
elif contrib_freq == "Monthly":
    interval = "1mo"
else:
    interval = "1mo"  # Default fallback (should not occur)

# Validate dates
if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

if end_date > datetime.now().date():
    st.error("End date cannot be in the future.")
    st.stop()

with st.spinner('Validating tickers and fetching data...'):
    # Clean and validate tickers
    tickers = [ticker.strip().upper() for ticker in tickers if ticker.strip()]
    if not tickers:
        st.error("Please enter at least one valid ticker symbol.")
        st.stop()
        
    index_ticker = index_ticker.strip().upper()
    if not index_ticker:
        st.error("Please enter a valid index ticker symbol.")
        st.stop()

    # Download data with progress updates
    progress_text = st.empty()
    
    progress_text.text("Downloading stock data...")
    stock_prices = download_data(tickers, start_date, end_date, interval)
    
    progress_text.text("Downloading index data...")
    index_prices = download_data(index_ticker, start_date, end_date, interval)
    
    if stock_prices.empty or index_prices.empty:
        st.error("Unable to proceed due to data download issues.")
        st.stop()
        
    progress_text.text("Performing calculations...")
    individual_portfolio_df = simulate_portfolio(stock_prices, contribution, initial_amount)
    index_portfolio_df = simulate_index_investment(index_prices, contribution, initial_amount)
    
    # Clear the progress text
    progress_text.empty()

st.subheader(f"Performance of Portfolio vs {index_ticker}")
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title('Consolidated Portfolio vs Single Asset Over Time')
ax.plot(individual_portfolio_df['Portfolio Value'], label='Portfolio (Selected Stocks)', color='blue', linewidth=2)
ax.plot(index_portfolio_df['Index Value'], label=f'{index_ticker}', color='green', linewidth=2)
ax.legend()
ax.set_xlabel('Time')
ax.set_ylabel('Portfolio Value (USD)')
ax.grid(True)
st.pyplot(fig)

st.subheader("Final Portfolio Values")
final_stock_value = individual_portfolio_df['Portfolio Value'].iloc[-1]
final_index_value = index_portfolio_df['Index Value'].iloc[-1]
total_invested_stocks = individual_portfolio_df['Total Invested'].iloc[-1]
total_invested_index = index_portfolio_df['Total Invested'].iloc[-1]

col1, col2 = st.columns(2)
with col1:
    st.metric("Selected Stocks Portfolio", f"${final_stock_value:,.2f}", 
              f"+${(final_stock_value - total_invested_stocks):,.2f} ({((final_stock_value / total_invested_stocks - 1) * 100):.2f}%)")
with col2:
    st.metric(f"{index_ticker}", f"${final_index_value:,.2f}", 
              f"+${(final_index_value - total_invested_index):,.2f} ({((final_index_value / total_invested_index - 1) * 100):.2f}%)")

st.write(f"**Total Invested:** ${total_invested_stocks:,.2f}")

st.download_button(
    label="Download Portfolio Data (CSV)",
    data=individual_portfolio_df.to_csv(),
    file_name='portfolio_data.csv',
    mime='text/csv',
)
st.write("Thanks for using my simulator, :red[Jose Cedeno]!")

st.markdown(
    """
    ---
    **Disclaimer:** This simulator is for informational and educational purposes only. 
    It is not financial advice, and should not be considered as a recommendation to buy or sell any specific securities. 
    Always conduct your own research and consult with a qualified financial advisor before making any investment decisions.
    """
)

st.markdown(
    """
    ---
    **Description:**

    This app's mathematical calculations center on modeling periodic investments using whole-share purchases and cash remainder handling. Here's a breakdown of the key computations:

    **Initialization with the Initial Investment:**  
    - The initial investment is divided evenly among the stocks (or applied wholly to the index).  
    - For each asset, the number of shares purchased is computed as:  
      **Number of Initial Shares = Floor(Initial Investment per Asset / Price at First Period)**  
    - Leftover cash is computed as the remainder:  
      **Leftover Cash = Initial Investment per Asset MOD Price at First Period**

    **Periodic Contributions and Purchase Calculations:**  
    - At each subsequent period, a fixed contribution is added to any cash left over from the previous period.  
    - For each asset in the portfolio, the calculation is:  
      **Total Money Available = Contribution (per asset, if multiple stocks) + Previous Leftover Cash**  
      **Additional Shares to Buy = Floor(Total Money Available / Current Price)**  
      **New Leftover Cash = Total Money Available MOD Current Price**  
    - The total number of shares held is updated cumulatively by adding the newly purchased whole shares.

    **Portfolio Valuation:**  
    - For every period, the current portfolio value is calculated by multiplying the total number of shares held by the asset's current price.  
    - For a multi-stock portfolio, this value is the sum across all assets.

    **Single Asset (Index) Calculation:**  
    - The same math is applied for a single asset: determining how many shares can be bought in each period, updating cumulative shares, and computing the portfolio value based on the current index price.

    **In summary**, the mathematical calculus involves:
    - Distributing investment amounts evenly (or fully when applicable).
    - Using floor division to ensure only whole shares are purchased.
    - Carrying over any remainder for future periods.
    - Updating the cumulative portfolio value by multiplying the total shares by the asset's current price.
    """
)
