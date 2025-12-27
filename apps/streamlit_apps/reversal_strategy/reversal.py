"""
Alpaca Reversal Pattern Scanner - Professional Trading Platform
Enhanced version with top 50 stocks and sector analysis
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import ta
import time
import warnings
warnings.filterwarnings('ignore')

# ==============================================================================
# PAGE CONFIGURATION
# ==============================================================================

st.set_page_config(
    page_title="Alpaca Pro Scanner",
    page_icon="assets/favicon.ico",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# PROFESSIONAL LIGHT THEME CSS
# ==============================================================================

st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main app background */
    .stApp {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container */
    .main {
        padding: 0rem 1rem;
        background-color: transparent;
    }
    
    /* Professional card styling */
    .pro-card {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    /* Header container */
    .header-container {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        padding: 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        border: 2px solid #2e5f8f;
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.3);
    }
    
    .header-container h1 {
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
    }
    
    .header-container p {
        color: #e3f2fd;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Signal badges with professional styling */
    .signal-long {
        background: linear-gradient(135deg, #00d084 0%, #00a06a 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 6px rgba(0, 208, 132, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-short {
        background: linear-gradient(135deg, #ff4757 0%, #d63447 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 6px rgba(255, 71, 87, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .signal-neutral {
        background: linear-gradient(135deg, #575b7a 0%, #404361 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 8px;
        font-weight: 600;
        display: inline-block;
        box-shadow: 0 4px 6px rgba(87, 91, 122, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    [data-testid="metric-container"] [data-testid="metric-label"] {
        color: #555555;
        font-weight: 500;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="metric-container"] [data-testid="metric-value"] {
        color: #1a1a1a;
        font-weight: 700;
        font-size: 1.8rem;
    }
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #00a86b;
        font-weight: 600;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #5b6cfd 0%, #4054f1 100%);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(91, 108, 253, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(91, 108, 253, 0.4);
        background: linear-gradient(135deg, #6b7cfd 0%, #5064f1 100%);
    }
    
    /* Sidebar styling */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f5f5f5 0%, #fafafa 100%);
        border-right: 2px solid #e0e0e0;
    }
    
    .css-1d391kg .stMarkdown h2, [data-testid="stSidebar"] .stMarkdown h2 {
        color: #1a1a1a;
        font-weight: 600;
        font-size: 1.2rem;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4a90e2;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 2px solid #d0d0d0;
        border-radius: 6px;
        padding: 0.5rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #4a90e2;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.15);
    }
    
    /* Tables */
    .dataframe {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 2px solid #e0e0e0;
        border-radius: 8px;
    }
    
    .dataframe thead th {
        background-color: #f5f5f5;
        color: #333333;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        padding: 1rem;
        border-bottom: 2px solid #4a90e2;
    }
    
    .dataframe tbody td {
        padding: 0.8rem;
        border-bottom: 1px solid #e8e8e8;
        color: #1a1a1a;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f5f5f5;
        border: 2px solid #d0d0d0;
        border-radius: 8px;
        color: #1a1a1a;
        font-weight: 600;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #e8e8e8;
        border-color: #4a90e2;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #f5f5f5;
        border-radius: 8px;
        padding: 0.25rem;
        gap: 0.5rem;
        border: 2px solid #e0e0e0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #555555;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: white;
    }
    
    /* Success/Warning/Error boxes */
    .stSuccess, .stWarning, .stError, .stInfo {
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid;
        background-color: #ffffff;
        color: #1a1a1a;
    }
    
    .stSuccess {
        border-left-color: #00a86b;
        background-color: rgba(0, 168, 107, 0.1);
        border: 2px solid rgba(0, 168, 107, 0.3);
    }
    
    .stWarning {
        border-left-color: #ff9500;
        background-color: rgba(255, 149, 0, 0.1);
        border: 2px solid rgba(255, 149, 0, 0.3);
    }
    
    .stError {
        border-left-color: #dc3545;
        background-color: rgba(220, 53, 69, 0.1);
        border: 2px solid rgba(220, 53, 69, 0.3);
    }
    
    .stInfo {
        border-left-color: #4a90e2;
        background-color: rgba(74, 144, 226, 0.1);
        border: 2px solid rgba(74, 144, 226, 0.3);
    }
    
    /* Sector badge */
    .sector-badge {
        background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
        color: #ffffff;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.3px;
        border: 1px solid #2e5f8f;
    }
    
    /* Stock grid cards */
    .stock-card {
        background: #ffffff;
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
        border-color: #4a90e2;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f5f5f5;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c0c0c0;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #4a90e2;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: #4a90e2;
    }
    
    /* Professional footer */
    .footer {
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
        border-radius: 12px;
        text-align: center;
        border: 2px solid #d0d0d0;
    }
    
    .footer p {
        color: #555555;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# TOP 50 LIQUID STOCKS WITH SECTORS
# ==============================================================================

TOP_50_STOCKS = {
    # Technology
    'AAPL': {'name': 'Apple Inc.', 'sector': 'Technology'},
    'MSFT': {'name': 'Microsoft Corp.', 'sector': 'Technology'},
    'NVDA': {'name': 'NVIDIA Corp.', 'sector': 'Technology'},
    'GOOGL': {'name': 'Alphabet Inc.', 'sector': 'Technology'},
    'META': {'name': 'Meta Platforms', 'sector': 'Technology'},
    'AVGO': {'name': 'Broadcom Inc.', 'sector': 'Technology'},
    'ORCL': {'name': 'Oracle Corp.', 'sector': 'Technology'},
    'ADBE': {'name': 'Adobe Inc.', 'sector': 'Technology'},
    'CRM': {'name': 'Salesforce', 'sector': 'Technology'},
    'AMD': {'name': 'AMD', 'sector': 'Technology'},
    'INTC': {'name': 'Intel Corp.', 'sector': 'Technology'},
    'QCOM': {'name': 'Qualcomm', 'sector': 'Technology'},
    
    # Consumer
    'AMZN': {'name': 'Amazon.com', 'sector': 'Consumer'},
    'TSLA': {'name': 'Tesla Inc.', 'sector': 'Consumer'},
    'WMT': {'name': 'Walmart', 'sector': 'Consumer'},
    'HD': {'name': 'Home Depot', 'sector': 'Consumer'},
    'MCD': {'name': 'McDonalds', 'sector': 'Consumer'},
    'NKE': {'name': 'Nike Inc.', 'sector': 'Consumer'},
    'SBUX': {'name': 'Starbucks', 'sector': 'Consumer'},
    
    # Financial
    'BRK-B': {'name': 'Berkshire Hathaway', 'sector': 'Financial'},
    'JPM': {'name': 'JPMorgan Chase', 'sector': 'Financial'},
    'V': {'name': 'Visa Inc.', 'sector': 'Financial'},
    'MA': {'name': 'Mastercard', 'sector': 'Financial'},
    'BAC': {'name': 'Bank of America', 'sector': 'Financial'},
    'WFC': {'name': 'Wells Fargo', 'sector': 'Financial'},
    'GS': {'name': 'Goldman Sachs', 'sector': 'Financial'},
    'MS': {'name': 'Morgan Stanley', 'sector': 'Financial'},
    'AXP': {'name': 'American Express', 'sector': 'Financial'},
    
    # Healthcare
    'LLY': {'name': 'Eli Lilly', 'sector': 'Healthcare'},
    'UNH': {'name': 'UnitedHealth', 'sector': 'Healthcare'},
    'JNJ': {'name': 'Johnson & Johnson', 'sector': 'Healthcare'},
    'PFE': {'name': 'Pfizer Inc.', 'sector': 'Healthcare'},
    'ABBV': {'name': 'AbbVie Inc.', 'sector': 'Healthcare'},
    'MRK': {'name': 'Merck & Co.', 'sector': 'Healthcare'},
    'TMO': {'name': 'Thermo Fisher', 'sector': 'Healthcare'},
    'ABT': {'name': 'Abbott Labs', 'sector': 'Healthcare'},
    
    # Energy
    'XOM': {'name': 'Exxon Mobil', 'sector': 'Energy'},
    'CVX': {'name': 'Chevron Corp.', 'sector': 'Energy'},
    'COP': {'name': 'ConocoPhillips', 'sector': 'Energy'},
    
    # Industrial
    'BA': {'name': 'Boeing Co.', 'sector': 'Industrial'},
    'CAT': {'name': 'Caterpillar', 'sector': 'Industrial'},
    'GE': {'name': 'General Electric', 'sector': 'Industrial'},
    'RTX': {'name': 'Raytheon', 'sector': 'Industrial'},
    
    # Entertainment & Communications
    'DIS': {'name': 'Walt Disney', 'sector': 'Entertainment'},
    'NFLX': {'name': 'Netflix Inc.', 'sector': 'Entertainment'},
    'CMCSA': {'name': 'Comcast Corp.', 'sector': 'Communications'},
    'VZ': {'name': 'Verizon', 'sector': 'Communications'},
    'T': {'name': 'AT&T Inc.', 'sector': 'Communications'},
    
    # Consumer Staples
    'PG': {'name': 'Procter & Gamble', 'sector': 'Consumer Staples'},
    'KO': {'name': 'Coca-Cola', 'sector': 'Consumer Staples'},
    'PEP': {'name': 'PepsiCo', 'sector': 'Consumer Staples'},
}

# ==============================================================================
# ENHANCED ALPACA SCANNER CLASS
# ==============================================================================

class AlpacaReversalScanner:
    """
    Professional reversal pattern scanner with sector analysis.
    """
    
    def __init__(self, api_key, api_secret, base_url):
        """Initialize Alpaca API connection."""
        try:
            self.api = tradeapi.REST(
                api_key,
                api_secret,
                base_url,
                api_version='v2'
            )
            self.connected = True
        except Exception as e:
            st.error(f"Failed to connect to Alpaca: {str(e)}")
            self.connected = False
    
    def check_market_status(self):
        """Check if market is open."""
        try:
            clock = self.api.get_clock()
            return clock.is_open, clock.next_open, clock.next_close
        except:
            return False, None, None
    
    def get_stock_info(self, symbol):
        """Get stock information including sector."""
        if symbol in TOP_50_STOCKS:
            return TOP_50_STOCKS[symbol]
        else:
            # For stocks not in our list, try to get basic info
            try:
                asset = self.api.get_asset(symbol)
                return {
                    'name': asset.name if hasattr(asset, 'name') else symbol,
                    'sector': 'Other'
                }
            except:
                return {'name': symbol, 'sector': 'Unknown'}
    
    def get_alpaca_data(self, symbol, timeframe='30Min', limit=500):
        """Fetch high-quality data from Alpaca - uses last available data when market is closed."""
        try:
            # Always get data up to current time, API will return last available
            end = datetime.now()
            start = end - timedelta(days=60)
            
            bars = self.api.get_bars(
                symbol,
                timeframe,
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d'),
                limit=limit,
                adjustment='raw'
            ).df
            
            if len(bars) == 0:
                return None
            
            # Convert to proper format
            bars.index = pd.to_datetime(bars.index)
            bars.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Trade_Count', 'VWAP']
            
            # Store last data timestamp for reference
            self.last_data_time = bars.index[-1]
            
            return bars
            
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return None
    
    def calculate_indicators(self, df):
        """Calculate all technical indicators."""
        # SMAs
        df['SMA65'] = df['Close'].rolling(window=65).mean()
        df['SMA182'] = df['Close'].rolling(window=182).mean()
        
        # Stochastic RSI
        rsi = ta.momentum.RSIIndicator(df['Close'], window=14)
        df['RSI'] = rsi.rsi()
        rsi_min = df['RSI'].rolling(window=14).min()
        rsi_max = df['RSI'].rolling(window=14).max()
        df['Stoch_RSI'] = 100 * (df['RSI'] - rsi_min) / (rsi_max - rsi_min + 0.0001)
        
        # Williams %R (WillyGeek)
        df['Williams_R'] = ta.momentum.WilliamsRIndicator(
            df['High'], df['Low'], df['Close'], lbp=21
        ).williams_r()
        
        # Williams %R EMA
        df['Williams_EMA'] = df['Williams_R'].ewm(span=13, adjust=False).mean()
        
        # Volume Analysis
        df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
        
        # ATR
        df['ATR'] = ta.volatility.AverageTrueRange(
            df['High'], df['Low'], df['Close'], window=14
        ).average_true_range()
        
        # Bollinger Bands
        bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
        df['BB_Upper'] = bb.bollinger_hband()
        df['BB_Lower'] = bb.bollinger_lband()
        
        return df
    
    def analyze_setup(self, df, symbol):
        """Analyze current setup for entry signals."""
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # Get stock info
        stock_info = self.get_stock_info(symbol)
        
        # Check LONG conditions
        long_conditions = {
            'Price > SMA65': last['Close'] > last['SMA65'],
            'Stoch RSI Oversold': last['Stoch_RSI'] < 30,
            'Stoch RSI Turning': last['Stoch_RSI'] > prev['Stoch_RSI'],
            'Williams %R < -70': last['Williams_R'] < -70,
            'Volume Surge': last['Volume_Ratio'] > 1.2,
            'SMA65 > SMA182': last['SMA65'] > last['SMA182']
        }
        
        # Check SHORT conditions
        short_conditions = {
            'Price < SMA65': last['Close'] < last['SMA65'],
            'Stoch RSI Overbought': last['Stoch_RSI'] > 70,
            'Stoch RSI Turning': last['Stoch_RSI'] < prev['Stoch_RSI'],
            'Williams %R > -30': last['Williams_R'] > -30,
            'Volume Surge': last['Volume_Ratio'] > 1.2,
            'SMA65 < SMA182': last['SMA65'] < last['SMA182']
        }
        
        # Calculate scores
        long_score = sum(long_conditions.values())
        short_score = sum(short_conditions.values())
        
        # Determine signal
        if long_score >= 4:
            signal_type = "LONG"
            score = long_score
            conditions_met = long_conditions
        elif short_score >= 4:
            signal_type = "SHORT"
            score = short_score
            conditions_met = short_conditions
        else:
            signal_type = "NO SIGNAL"
            score = max(long_score, short_score)
            conditions_met = long_conditions if long_score > short_score else short_conditions
        
        # Calculate risk management
        atr = last['ATR']
        
        if signal_type == "LONG":
            stop_loss = last['Close'] - (atr * 1.5)
            target1 = last['Close'] + (atr * 2)
            target2 = last['Close'] + (atr * 3)
        elif signal_type == "SHORT":
            stop_loss = last['Close'] + (atr * 1.5)
            target1 = last['Close'] - (atr * 2)
            target2 = last['Close'] - (atr * 3)
        else:
            stop_loss = last['Close'] - (atr * 1.5)
            target1 = last['Close'] + (atr * 2)
            target2 = last['Close'] + (atr * 3)
        
        risk = abs(last['Close'] - stop_loss)
        reward = abs(target1 - last['Close'])
        risk_reward = round(reward / risk, 2) if risk > 0 else 0
        
        return {
            'symbol': symbol,
            'name': stock_info['name'],
            'sector': stock_info['sector'],
            'signal': signal_type,
            'score': score,
            'max_score': 6,
            'price': round(last['Close'], 2),
            'stop_loss': round(stop_loss, 2),
            'target1': round(target1, 2),
            'target2': round(target2, 2),
            'risk': round(risk, 2),
            'risk_reward': risk_reward,
            'stoch_rsi': round(last['Stoch_RSI'], 1),
            'williams_r': round(last['Williams_R'], 1),
            'williams_ema': round(last['Williams_EMA'], 1),
            'volume_ratio': round(last['Volume_Ratio'], 2),
            'conditions': conditions_met,
            'vwap': round(last['VWAP'], 2) if 'VWAP' in df.columns else None,
            'sma65': round(last['SMA65'], 2),
            'sma182': round(last['SMA182'], 2)
        }
    
    def scan_multiple_stocks(self, symbols, progress_bar=None):
        """Scan multiple stocks and return results."""
        results = []
        
        for i, symbol in enumerate(symbols):
            if progress_bar:
                progress_bar.progress((i + 1) / len(symbols))
            
            df = self.get_alpaca_data(symbol, timeframe='30Min')
            
            if df is not None and len(df) >= 200:
                df = self.calculate_indicators(df)
                df = df.dropna()
                
                if len(df) > 0:
                    analysis = self.analyze_setup(df, symbol)
                    results.append(analysis)
            
            time.sleep(0.1)  # Rate limiting
        
        return results

# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================

def create_professional_chart(df, symbol, analysis):
    """Create professional interactive chart with dark theme."""
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.5, 0.15, 0.15, 0.15],
        subplot_titles=(
            f"{symbol} - {analysis['name']} ({analysis['sector']})",
            'Volume Analysis',
            'Stochastic RSI',
            'Williams %R (WillyGeek)'
        )
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Price',
            increasing_line_color='#00d084',
            decreasing_line_color='#ff4757'
        ),
        row=1, col=1
    )
    
    # Add SMAs
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA65'], name='SMA65', 
                   line=dict(color='#ff9800', width=2)),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA182'], name='SMA182', 
                   line=dict(color='#ff4757', width=2)),
        row=1, col=1
    )
    
    # Add VWAP
    if 'VWAP' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['VWAP'], name='VWAP', 
                       line=dict(color='#9c27b0', width=1, dash='dot')),
            row=1, col=1
        )
    
    # Volume with colors
    colors = ['#00d084' if df['Close'].iloc[i] >= df['Open'].iloc[i] else '#ff4757' 
              for i in range(len(df))]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', 
               marker_color=colors, opacity=0.7),
        row=2, col=1
    )
    
    # Volume SMA
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Volume_SMA'], name='Vol SMA', 
                   line=dict(color='#ffa502', width=1)),
        row=2, col=1
    )
    
    # Stochastic RSI
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Stoch_RSI'], name='Stoch RSI',
                   line=dict(color='#00d2d3', width=2)),
        row=3, col=1
    )
    fig.add_hline(y=80, line_dash="dash", line_color="#ff4757", 
                  line_width=1, row=3, col=1)
    fig.add_hline(y=20, line_dash="dash", line_color="#00d084", 
                  line_width=1, row=3, col=1)
    
    # Williams %R with EMA
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Williams_R'], name='Williams %R',
                   line=dict(color='#ffd93d', width=2)),
        row=4, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Williams_EMA'], name='Williams EMA',
                   line=dict(color='#00d2d3', width=1, dash='dot')),
        row=4, col=1
    )
    fig.add_hline(y=-20, line_dash="dash", line_color="#ff4757", 
                  line_width=1, row=4, col=1)
    fig.add_hline(y=-80, line_dash="dash", line_color="#00d084", 
                  line_width=1, row=4, col=1)
    
    # Update layout with professional dark theme
    fig.update_layout(
        template='plotly_dark',
        height=900,
        showlegend=True,
        hovermode='x unified',
        paper_bgcolor='#1e2139',
        plot_bgcolor='#151932',
        font=dict(family='Inter', color='#8b92b9'),
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Update axes
    fig.update_xaxes(gridcolor='#2d3153', gridwidth=1)
    fig.update_yaxes(gridcolor='#2d3153', gridwidth=1)
    
    # Update y-axes labels
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    fig.update_yaxes(title_text="Stoch RSI %", row=3, col=1)
    fig.update_yaxes(title_text="Williams %R", row=4, col=1)
    
    return fig

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

def main():
    # Initialize session state
    if 'scanner' not in st.session_state:
        st.session_state.scanner = None
    if 'last_analysis' not in st.session_state:
        st.session_state.last_analysis = None
    if 'scan_history' not in st.session_state:
        st.session_state.scan_history = []
    if 'batch_results' not in st.session_state:
        st.session_state.batch_results = None
    
    # Professional Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("assets/logo.png", width=150)
        except:
            pass
        st.markdown("""
        <div class='header-container'>
            <h1>ALPACA PRO SCANNER</h1>
            <p>Professional Reversal Pattern Detection System</p>
        </div>
        """, unsafe_allow_html=True)
    
    # API Connection Status Box (Dark Blue)
    if st.session_state.scanner and st.session_state.scanner.connected:
        is_open, next_open, next_close = st.session_state.scanner.check_market_status()
        
        # Get last data time if available
        last_data_info = ""
        if hasattr(st.session_state.scanner, 'last_data_time'):
            last_data_info = f" | Última data: {st.session_state.scanner.last_data_time.strftime('%Y-%m-%d %H:%M')}"
        
        status_html = f"""
        <div style='background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border: 2px solid #2563eb;
                    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
                    margin-bottom: 2rem;
                    text-align: center;'>
            <div style='display: flex; justify-content: center; align-items: center; gap: 2rem; flex-wrap: wrap;'>
                <div style='color: #ffffff; font-size: 1.1rem; font-weight: 600;'>
                    <span style='color: #10b981; font-size: 1.3rem; margin-right: 8px;'>●</span>
                    API CONECTADA
                </div>
                <div style='color: #93c5fd; font-size: 0.95rem; font-weight: 500;'>
                    {'🟢 Mercado ABIERTO' if is_open else '🔴 Mercado CERRADO'}
                    {' - Usando última data disponible' if not is_open else ''}
                    {last_data_info}
                </div>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
    elif st.session_state.scanner and not st.session_state.scanner.connected:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border: 2px solid #dc2626;
                    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
                    margin-bottom: 2rem;
                    text-align: center;'>
            <div style='color: #ffffff; font-size: 1.1rem; font-weight: 600;'>
                <span style='color: #ef4444; font-size: 1.3rem; margin-right: 8px;'>●</span>
                API DESCONECTADA - Verifica tus credenciales
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #78350f 0%, #92400e 100%); 
                    padding: 1.5rem; 
                    border-radius: 12px; 
                    border: 2px solid #d97706;
                    box-shadow: 0 4px 12px rgba(217, 119, 6, 0.3);
                    margin-bottom: 2rem;
                    text-align: center;'>
            <div style='color: #ffffff; font-size: 1.1rem; font-weight: 600;'>
                <span style='color: #fbbf24; font-size: 1.3rem; margin-right: 8px;'>●</span>
                ESPERANDO CONEXIÓN - Configura la API en el panel lateral
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration Panel")
        
        # API Connection
        with st.expander("🔐 API Credentials", expanded=True):
            api_key = st.text_input("API Key", value="PK3O2J7KSHRME7LI95AB", type="password")
            api_secret = st.text_input("API Secret", 
                                      value="gjXeodXRbJZ9LT3gqSPRHMfFsjCBaTSS7lXE1hws", 
                                      type="password")
            base_url = st.selectbox("Environment", 
                                   ["https://paper-api.alpaca.markets", 
                                    "https://api.alpaca.markets"],
                                   index=0)
            
            if st.button("🔌 Connect", use_container_width=True):
                with st.spinner("Establishing connection..."):
                    st.session_state.scanner = AlpacaReversalScanner(api_key, api_secret, base_url)
                    if st.session_state.scanner.connected:
                        st.success("✅ Connected to Alpaca Markets")
                        time.sleep(1)
                        st.rerun()
        
        # Market Status Display
        if st.session_state.scanner and st.session_state.scanner.connected:
            st.markdown("---")
            st.markdown("## 📊 Market Status")
            is_open, next_open, next_close = st.session_state.scanner.check_market_status()
            
            if is_open:
                st.success("🟢 Market OPEN")
                if next_close:
                    st.info(f"Closes: {next_close.strftime('%H:%M ET')}")
            else:
                st.error("🔴 Market CLOSED")
                if next_open:
                    st.info(f"Opens: {next_open.strftime('%m/%d %H:%M ET')}")
        
        # Quick Actions
        st.markdown("---")
        st.markdown("## 🚀 Quick Actions")
        
        scan_mode = st.radio(
            "Scan Mode",
            ["Single Stock", "Top 50 Stocks", "Custom List"],
            index=0
        )
        
        # Sector Filter for Top 50
        if scan_mode == "Top 50 Stocks":
            st.markdown("### Filter by Sector")
            sectors = list(set([stock['sector'] for stock in TOP_50_STOCKS.values()]))
            selected_sectors = st.multiselect(
                "Select Sectors",
                sectors,
                default=sectors[:3]
            )
    
    # Main Content Area
    if st.session_state.scanner and st.session_state.scanner.connected:
        
        # Scan Controls
        st.markdown("<div class='pro-card'>", unsafe_allow_html=True)
        
        if scan_mode == "Single Stock":
            col1, col2 = st.columns([3, 1])
            with col1:
                symbol = st.text_input("📊 Enter Stock Symbol", 
                                     placeholder="e.g., AAPL, TSLA, ASTS")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                scan_button = st.button("🔍 SCAN", use_container_width=True, 
                                       disabled=not symbol)
            
            if scan_button and symbol:
                with st.spinner(f"Analyzing {symbol.upper()}..."):
                    df = st.session_state.scanner.get_alpaca_data(symbol.upper(), '30Min')
                    
                    if df is not None and len(df) >= 200:
                        df = st.session_state.scanner.calculate_indicators(df)
                        df = df.dropna()
                        
                        analysis = st.session_state.scanner.analyze_setup(df, symbol.upper())
                        st.session_state.last_analysis = (analysis, df)
                        
                        # Add to history
                        st.session_state.scan_history.append({
                            'Time': datetime.now().strftime("%H:%M"),
                            'Symbol': symbol.upper(),
                            'Sector': analysis['sector'],
                            'Signal': analysis['signal'],
                            'Score': f"{analysis['score']}/{analysis['max_score']}",
                            'Price': f"${analysis['price']}"
                        })
                    else:
                        st.error(f"❌ Insufficient data for {symbol}")
        
        elif scan_mode == "Top 50 Stocks":
            if st.button("🚀 SCAN TOP 50 STOCKS", use_container_width=True):
                # Filter stocks by selected sectors
                filtered_stocks = [symbol for symbol, info in TOP_50_STOCKS.items() 
                                  if info['sector'] in selected_sectors]
                
                st.info(f"Scanning {len(filtered_stocks)} stocks from selected sectors...")
                progress_bar = st.progress(0)
                
                with st.spinner("Scanning in progress..."):
                    results = st.session_state.scanner.scan_multiple_stocks(
                        filtered_stocks, progress_bar
                    )
                    st.session_state.batch_results = results
                    progress_bar.progress(1.0)
                    st.success(f"✅ Scan complete! Found {len([r for r in results if r['signal'] != 'NO SIGNAL'])} signals")
        
        elif scan_mode == "Custom List":
            custom_symbols = st.text_area("Enter symbols (one per line)", 
                                         placeholder="AAPL\nTSLA\nNVDA")
            if st.button("🔍 SCAN CUSTOM LIST", use_container_width=True):
                symbols = [s.strip().upper() for s in custom_symbols.split('\n') if s.strip()]
                if symbols:
                    progress_bar = st.progress(0)
                    with st.spinner(f"Scanning {len(symbols)} stocks..."):
                        results = st.session_state.scanner.scan_multiple_stocks(
                            symbols, progress_bar
                        )
                        st.session_state.batch_results = results
                        st.success("✅ Scan complete!")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Display Batch Results
        if st.session_state.batch_results:
            st.markdown("---")
            st.markdown("## 📊 Scan Results")
            
            # Filter results
            long_signals = [r for r in st.session_state.batch_results if r['signal'] == 'LONG']
            short_signals = [r for r in st.session_state.batch_results if r['signal'] == 'SHORT']
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Scanned", len(st.session_state.batch_results))
            with col2:
                st.metric("Long Signals", len(long_signals), delta="Bullish")
            with col3:
                st.metric("Short Signals", len(short_signals), delta="Bearish")
            with col4:
                st.metric("Strong Signals", 
                         len([r for r in st.session_state.batch_results if r['score'] >= 5]),
                         delta="5+ Score")
            
            # Display results in tabs
            tab1, tab2, tab3 = st.tabs(["🟢 Long Signals", "🔴 Short Signals", "📋 All Results"])
            
            with tab1:
                if long_signals:
                    for signal in sorted(long_signals, key=lambda x: x['score'], reverse=True):
                        with st.expander(f"{signal['symbol']} - Score: {signal['score']}/6 ⭐"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**{signal['name']}**")
                                st.markdown(f"<span class='sector-badge'>{signal['sector']}</span>", 
                                          unsafe_allow_html=True)
                            with col2:
                                st.metric("Entry", f"${signal['price']}")
                                st.metric("Stop Loss", f"${signal['stop_loss']}")
                            with col3:
                                st.metric("Target 1", f"${signal['target1']}")
                                st.metric("R:R Ratio", signal['risk_reward'])
                else:
                    st.info("No long signals found")
            
            with tab2:
                if short_signals:
                    for signal in sorted(short_signals, key=lambda x: x['score'], reverse=True):
                        with st.expander(f"{signal['symbol']} - Score: {signal['score']}/6 ⭐"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**{signal['name']}**")
                                st.markdown(f"<span class='sector-badge'>{signal['sector']}</span>", 
                                          unsafe_allow_html=True)
                            with col2:
                                st.metric("Entry", f"${signal['price']}")
                                st.metric("Stop Loss", f"${signal['stop_loss']}")
                            with col3:
                                st.metric("Target 1", f"${signal['target1']}")
                                st.metric("R:R Ratio", signal['risk_reward'])
                else:
                    st.info("No short signals found")
            
            with tab3:
                # Create DataFrame for all results
                df_results = pd.DataFrame(st.session_state.batch_results)
                df_display = df_results[['symbol', 'name', 'sector', 'signal', 'score', 
                                        'price', 'risk_reward']].copy()
                df_display['score'] = df_display['score'].astype(str) + '/6'
                st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Display Single Analysis
        if st.session_state.last_analysis:
            analysis, df = st.session_state.last_analysis
            
            st.markdown("---")
            
            # Signal Header with Sector
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"### {analysis['symbol']}")
                st.markdown(f"**{analysis['name']}**")
                st.markdown(f"<span class='sector-badge'>{analysis['sector']}</span>", 
                          unsafe_allow_html=True)
                
                if analysis['signal'] == "LONG":
                    st.markdown("<span class='signal-long'>LONG SIGNAL</span>", 
                              unsafe_allow_html=True)
                elif analysis['signal'] == "SHORT":
                    st.markdown("<span class='signal-short'>SHORT SIGNAL</span>", 
                              unsafe_allow_html=True)
                else:
                    st.markdown("<span class='signal-neutral'>NO SIGNAL</span>", 
                              unsafe_allow_html=True)
            
            with col2:
                st.metric("Signal Strength", f"{analysis['score']}/{analysis['max_score']}", 
                         delta=f"{'⭐' * analysis['score']}")
                st.metric("Price vs SMA65", 
                         "Above" if analysis['price'] > analysis['sma65'] else "Below",
                         delta=f"${round(analysis['price'] - analysis['sma65'], 2)}")
            
            with col3:
                st.metric("Entry Price", f"${analysis['price']}")
                st.metric("Risk/Reward", f"1:{analysis['risk_reward']}", 
                         delta="Good" if analysis['risk_reward'] >= 1.5 else "Fair")
            
            with col4:
                st.metric("Stop Loss", f"${analysis['stop_loss']}", 
                         delta=f"-${analysis['risk']}")
                st.metric("Target 1", f"${analysis['target1']}", 
                         delta=f"+${round(analysis['target1'] - analysis['price'], 2)}")
            
            # Professional Tabs
            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["📊 Chart", "📈 Analysis", "✅ Conditions", "📋 Indicators", "💡 Strategy"]
            )
            
            with tab1:
                fig = create_professional_chart(df.tail(200), analysis['symbol'], analysis)
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🎯 Trade Setup")
                    setup_data = {
                        'Level': ['Entry', 'Stop Loss', 'Target 1', 'Target 2'],
                        'Price': [f"${analysis['price']}", 
                                 f"${analysis['stop_loss']}", 
                                 f"${analysis['target1']}", 
                                 f"${analysis['target2']}"],
                        'Distance': ['—', 
                                    f"-${analysis['risk']}", 
                                    f"+${round(analysis['target1'] - analysis['price'], 2)}", 
                                    f"+${round(analysis['target2'] - analysis['price'], 2)}"]
                    }
                    st.table(pd.DataFrame(setup_data))
                
                with col2:
                    st.markdown("### 📊 Market Position")
                    position_data = {
                        'Metric': ['SMA65', 'SMA182', 'VWAP', 'ATR'],
                        'Value': [f"${analysis['sma65']}", 
                                 f"${analysis['sma182']}", 
                                 f"${analysis['vwap']}" if analysis['vwap'] else "N/A",
                                 f"${round(df['ATR'].iloc[-1], 2)}"],
                        'Status': [
                            '🟢' if analysis['price'] > analysis['sma65'] else '🔴',
                            '🟢' if analysis['sma65'] > analysis['sma182'] else '🔴',
                            '🟢' if analysis['price'] < analysis['vwap'] else '🔴' if analysis['vwap'] else '—',
                            '—'
                        ]
                    }
                    st.table(pd.DataFrame(position_data))
            
            with tab3:
                st.markdown("### Signal Conditions Analysis")
                
                conditions_df = pd.DataFrame([
                    {'Condition': cond, 'Status': '✅' if met else '❌', 'Met': met}
                    for cond, met in analysis['conditions'].items()
                ])
                
                st.dataframe(conditions_df, use_container_width=True, hide_index=True)
                
                # Signal strength gauge
                met_count = sum(analysis['conditions'].values())
                if met_count >= 5:
                    st.success(f"💪 Strong Signal: {met_count}/6 conditions met")
                elif met_count >= 4:
                    st.warning(f"⚠️ Moderate Signal: {met_count}/6 conditions met")
                else:
                    st.error(f"❌ Weak Signal: {met_count}/6 conditions met (need 4+)")
            
            with tab4:
                st.markdown("### Technical Indicators")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Momentum Indicators")
                    momentum_data = {
                        'Indicator': ['Stoch RSI', 'Williams %R', 'Williams EMA', 'RSI'],
                        'Value': [f"{analysis['stoch_rsi']}%", 
                                 f"{analysis['williams_r']}%",
                                 f"{analysis['williams_ema']}%",
                                 f"{round(df['RSI'].iloc[-1], 1)}%"],
                        'Zone': [
                            'Oversold' if analysis['stoch_rsi'] < 30 else 'Overbought' if analysis['stoch_rsi'] > 70 else 'Neutral',
                            'Oversold' if analysis['williams_r'] < -70 else 'Overbought' if analysis['williams_r'] > -30 else 'Neutral',
                            '—',
                            'Oversold' if df['RSI'].iloc[-1] < 30 else 'Overbought' if df['RSI'].iloc[-1] > 70 else 'Neutral'
                        ]
                    }
                    st.table(pd.DataFrame(momentum_data))
                
                with col2:
                    st.markdown("#### Volume & Trend")
                    volume_data = {
                        'Indicator': ['Volume Ratio', 'Volume SMA', 'Price Trend', 'SMA Trend'],
                        'Value': [f"{analysis['volume_ratio']}x", 
                                 f"{round(df['Volume_SMA'].iloc[-1]/1000000, 2)}M",
                                 'Bullish' if analysis['price'] > analysis['sma65'] else 'Bearish',
                                 'Bullish' if analysis['sma65'] > analysis['sma182'] else 'Bearish'],
                        'Signal': [
                            '🟢 High' if analysis['volume_ratio'] > 1.2 else '⚪ Normal',
                            '—',
                            '🟢' if analysis['price'] > analysis['sma65'] else '🔴',
                            '🟢' if analysis['sma65'] > analysis['sma182'] else '🔴'
                        ]
                    }
                    st.table(pd.DataFrame(volume_data))
            
            with tab5:
                st.markdown("### 💡 Trading Strategy")
                
                if analysis['signal'] != "NO SIGNAL":
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info(f"""
                        **Entry Strategy:**
                        • Signal Type: {analysis['signal']}
                        • Entry Price: ${analysis['price']}
                        • Position Size: {2 if analysis['score'] >= 5 else 1}% of capital
                        • Entry Method: {'Market order' if analysis['score'] >= 5 else 'Limit order'}
                        
                        **Timing:**
                        • Best Hours: 10:00 AM - 3:00 PM ET
                        • Avoid: First/Last 30 minutes
                        • Hold Time: 2-8 hours typical
                        """)
                    
                    with col2:
                        st.warning(f"""
                        **Risk Management:**
                        • Stop Loss: ${analysis['stop_loss']}
                        • Max Risk: ${analysis['risk']}/share
                        • Position Risk: {2 if analysis['score'] >= 5 else 1}% of account
                        
                        **Profit Taking:**
                        • Target 1: ${analysis['target1']} (50% position)
                        • Target 2: ${analysis['target2']} (50% position)
                        • Trail stop after T1 hit
                        """)
                else:
                    st.warning("""
                    ⚠️ **No Clear Setup - Wait for Better Entry**
                    
                    Current conditions don't meet minimum requirements.
                    Monitor for:
                    • Price approaching SMA65
                    • Stoch RSI entering extreme zones
                    • Williams %R divergence
                    • Volume surge on reversal
                    """)
    
    else:
        # Connection required
        st.warning("⚠️ Please connect to Alpaca API to begin scanning")
        
        # Feature showcase
        st.markdown("---")
        st.markdown("## 🌟 Platform Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class='pro-card'>
            <h3>📊 Top 50 Stocks</h3>
            <p>Scan the most liquid stocks across all major sectors</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class='pro-card'>
            <h3>🎯 Sector Analysis</h3>
            <p>Filter and analyze stocks by industry sector</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class='pro-card'>
            <h3>📈 Professional Charts</h3>
            <p>Interactive charts with all key indicators</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Professional Footer
    st.markdown("""
    <div class='footer'>
        <p><strong>Alpaca Pro Scanner</strong> | Professional Trading Platform</p>
        <p>Powered by Alpaca Markets API | Real-time market data</p>
        <p>⚠️ Trading involves risk. Past performance does not guarantee future results.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
