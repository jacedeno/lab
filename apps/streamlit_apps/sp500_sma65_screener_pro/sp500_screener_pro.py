import streamlit as st
import pandas as pd
import numpy as np
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
from pathlib import Path

# --- Page Configuration ---
st.set_page_config(
    page_title="S&P 500 SMA Screener Pro",
    page_icon="assets/favicon.png",  # Your favicon
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS Styling with Dark Blue Theme ---
def load_custom_css():
    st.markdown("""
        <style>
        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        /* Root Variables - Dark Blue Color Palette */
        :root {
            --primary-blue: #0A2647;
            --secondary-blue: #144272;
            --accent-blue: #205295;
            --light-blue: #2C74B3;
            --text-white: #FFFFFF;
            --text-gray: #B8C5D6;
            --success-green: #00D9A5;
            --warning-yellow: #FFB800;
            --danger-red: #FF6B6B;
            --card-bg: #1a1f3a;
            --hover-bg: #253557;
        }
        
        /* Global Styles */
        * {
            font-family: 'Inter', sans-serif;
        }
        
        /* Main Background */
        .stApp {
            background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
        }
        
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, var(--secondary-blue) 0%, var(--primary-blue) 100%);
            border-right: 2px solid var(--accent-blue);
        }
        
        [data-testid="stSidebar"] .element-container {
            color: var(--text-white);
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-white) !important;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        h1 {
            font-size: 2.5rem !important;
            margin-bottom: 0.5rem !important;
            background: linear-gradient(90deg, #2C74B3 0%, #00D9A5 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* Tabs Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: var(--card-bg);
            padding: 10px;
            border-radius: 10px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background-color: transparent;
            border-radius: 8px;
            color: var(--text-gray);
            padding: 12px 24px;
            font-weight: 600;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: var(--hover-bg);
            color: var(--text-white);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--light-blue) 100%);
            color: var(--text-white) !important;
            border: 2px solid var(--light-blue);
        }
        
        /* Cards & Containers */
        .element-container {
            color: var(--text-white);
        }
        
        div[data-testid="stMetricValue"] {
            color: var(--light-blue) !important;
            font-size: 2rem !important;
            font-weight: 700 !important;
        }
        
        div[data-testid="stMetricLabel"] {
            color: var(--text-gray) !important;
            font-weight: 600 !important;
            font-size: 0.9rem !important;
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--light-blue) 100%);
            color: var(--text-white);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(44, 116, 179, 0.3);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(44, 116, 179, 0.5);
            background: linear-gradient(135deg, var(--light-blue) 0%, var(--accent-blue) 100%);
        }
        
        .stButton > button:active {
            transform: translateY(0px);
        }
        
        /* Primary Button */
        button[kind="primary"] {
            background: linear-gradient(135deg, var(--success-green) 0%, #00B887 100%) !important;
            box-shadow: 0 4px 15px rgba(0, 217, 165, 0.3) !important;
        }
        
        button[kind="primary"]:hover {
            background: linear-gradient(135deg, #00B887 0%, var(--success-green) 100%) !important;
            box-shadow: 0 6px 20px rgba(0, 217, 165, 0.5) !important;
        }
        
        /* Input Fields */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select {
            background-color: var(--card-bg);
            color: var(--text-white);
            border: 2px solid var(--accent-blue);
            border-radius: 8px;
            padding: 10px;
            font-size: 1rem;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus {
            border-color: var(--light-blue);
            box-shadow: 0 0 0 3px rgba(44, 116, 179, 0.2);
        }
        
        /* Sliders */
        .stSlider > div > div > div {
            background-color: var(--accent-blue);
        }
        
        .stSlider > div > div > div > div {
            background-color: var(--light-blue);
        }
        
        /* Dataframe */
        .dataframe {
            background-color: var(--card-bg) !important;
            color: var(--text-white) !important;
            border-radius: 10px !important;
            overflow: hidden;
        }
        
        .dataframe thead tr th {
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--light-blue) 100%) !important;
            color: var(--text-white) !important;
            font-weight: 700 !important;
            padding: 15px !important;
            border: none !important;
        }
        
        .dataframe tbody tr {
            background-color: var(--card-bg) !important;
            border-bottom: 1px solid var(--accent-blue) !important;
            transition: all 0.2s ease;
        }
        
        .dataframe tbody tr:hover {
            background-color: var(--hover-bg) !important;
            transform: scale(1.01);
        }
        
        .dataframe tbody tr td {
            color: var(--text-white) !important;
            padding: 12px !important;
        }
        
        /* Info/Success/Warning/Error Boxes */
        .stAlert {
            background-color: var(--card-bg);
            border-left: 4px solid var(--light-blue);
            border-radius: 8px;
            padding: 15px;
            color: var(--text-white);
        }
        
        div[data-baseweb="notification"] {
            background-color: var(--card-bg);
            border-radius: 8px;
            border-left: 4px solid var(--light-blue);
        }
        
        .stSuccess {
            border-left-color: var(--success-green) !important;
        }
        
        .stWarning {
            border-left-color: var(--warning-yellow) !important;
        }
        
        .stError {
            border-left-color: var(--danger-red) !important;
        }
        
        /* Progress Bar */
        .stProgress > div > div > div {
            background: linear-gradient(90deg, var(--accent-blue) 0%, var(--success-green) 100%);
            border-radius: 10px;
        }
        
        /* Checkbox */
        .stCheckbox > label {
            color: var(--text-white) !important;
        }
        
        /* Expander */
        .streamlit-expanderHeader {
            background-color: var(--card-bg);
            color: var(--text-white);
            border-radius: 8px;
            font-weight: 600;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: var(--hover-bg);
        }
        
        /* Download Button */
        .stDownloadButton > button {
            background: linear-gradient(135deg, var(--warning-yellow) 0%, #FF9500 100%);
            color: var(--primary-blue);
            font-weight: 700;
        }
        
        .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #FF9500 0%, var(--warning-yellow) 100%);
            box-shadow: 0 6px 20px rgba(255, 184, 0, 0.5);
        }
        
        /* Custom Card Class */
        .custom-card {
            background: linear-gradient(135deg, var(--card-bg) 0%, var(--secondary-blue) 100%);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid var(--accent-blue);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        
        .custom-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 35px rgba(44, 116, 179, 0.4);
            border-color: var(--light-blue);
        }
        
        /* Status Badge */
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            margin: 5px;
        }
        
        .status-success {
            background-color: var(--success-green);
            color: var(--primary-blue);
        }
        
        .status-warning {
            background-color: var(--warning-yellow);
            color: var(--primary-blue);
        }
        
        .status-danger {
            background-color: var(--danger-red);
            color: var(--text-white);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--primary-blue);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--accent-blue);
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--light-blue);
        }
        
        /* Logo Container */
        .logo-container {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px 0;
            margin-bottom: 20px;
        }
        
        .logo-container img {
            max-width: 200px;
            filter: drop-shadow(0 4px 15px rgba(44, 116, 179, 0.5));
            transition: all 0.3s ease;
        }
        
        .logo-container img:hover {
            transform: scale(1.05);
            filter: drop-shadow(0 6px 20px rgba(44, 116, 179, 0.7));
        }
        
        /* Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .animated-card {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Form Styling */
        .stForm {
            background-color: var(--card-bg);
            padding: 25px;
            border-radius: 15px;
            border: 2px solid var(--accent-blue);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }
        
        /* Selectbox */
        div[data-baseweb="select"] > div {
            background-color: var(--card-bg);
            border-color: var(--accent-blue);
            color: var(--text-white);
        }
        
        /* Time Input */
        .stTimeInput > div > div > input {
            background-color: var(--card-bg);
            color: var(--text-white);
            border: 2px solid var(--accent-blue);
        }
        
        </style>
    """, unsafe_allow_html=True)

# --- Logo and Header Component ---
def display_logo_header():
    """Display logo and app header"""
    # Check if logo exists
    logo_path = Path("assets/logo.png")
    
    if logo_path.exists():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image("assets/logo.png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        # Fallback if logo doesn't exist
        st.markdown("""
            <div style="text-align: center; padding: 30px 0;">
                <h1 style="font-size: 3.5rem; margin-bottom: 0;">
                    📈 S&P 500 SMA Screener Pro
                </h1>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="text-align: center; color: var(--text-gray); margin-bottom: 30px;">
            <p style="font-size: 1.2rem; font-weight: 300;">
                Advanced stock screening with AI-powered insights • Real-time Alpaca data • Professional grade analytics
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

# --- Custom Components ---
def create_metric_card(label, value, delta=None, icon="📊"):
    """Create a custom styled metric card"""
    delta_html = ""
    if delta:
        delta_color = "var(--success-green)" if delta > 0 else "var(--danger-red)"
        delta_symbol = "↑" if delta > 0 else "↓"
        delta_html = f'<div style="color: {delta_color}; font-size: 0.9rem; font-weight: 600;">{delta_symbol} {abs(delta):.2f}%</div>'
    
    return f"""
        <div class="custom-card animated-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <div style="color: var(--text-gray); font-size: 0.9rem; font-weight: 600; margin-bottom: 5px;">
                        {icon} {label}
                    </div>
                    <div style="color: var(--light-blue); font-size: 2rem; font-weight: 700;">
                        {value}
                    </div>
                    {delta_html}
                </div>
            </div>
        </div>
    """

def create_status_badge(status, text):
    """Create a status badge"""
    status_class = f"status-{status}"
    return f'<span class="status-badge {status_class}">{text}</span>'

# --- Database Setup ---
def init_database():
    """Initialize SQLite database for favorites and scan history"""
    conn = sqlite3.connect('screener_data.db', check_same_thread=False)
    c = conn.cursor()
    
    # Favorites table
    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (symbol TEXT PRIMARY KEY, 
                  company TEXT,
                  added_date TEXT,
                  notes TEXT)''')
    
    # Scan history table
    c.execute('''CREATE TABLE IF NOT EXISTS scan_history
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  scan_date TEXT,
                  symbol TEXT,
                  price REAL,
                  pct_above_65 REAL,
                  pct_above_182 REAL,
                  volume REAL,
                  market_cap REAL,
                  sector TEXT)''')
    
    # Email settings table
    c.execute('''CREATE TABLE IF NOT EXISTS email_settings
                 (id INTEGER PRIMARY KEY,
                  email TEXT,
                  smtp_server TEXT,
                  smtp_port INTEGER,
                  smtp_username TEXT,
                  smtp_password TEXT,
                  enabled INTEGER)''')
    
    # Scheduled scan settings
    c.execute('''CREATE TABLE IF NOT EXISTS scan_schedule
                 (id INTEGER PRIMARY KEY,
                  enabled INTEGER,
                  scan_time TEXT,
                  last_run TEXT)''')
    
    conn.commit()
    return conn

# Initialize database
conn = init_database()

# --- Alpaca API Credentials ---
API_KEY = "PK3O2J7KSHRME7LI95AB"
API_SECRET = "gjXeodXRbJZ9LT3gqSPRHMfFsjCBaTSS7lXE1hws"

# Initialize Alpaca client
@st.cache_resource
def get_alpaca_client():
    return StockHistoricalDataClient(API_KEY, API_SECRET)

# --- Load S&P 500 List with Additional Info ---
@st.cache_data(ttl=86400)
def load_sp500_symbols():
    """Load S&P 500 symbols with sector and market cap info"""
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        # Add headers to avoid 403 Forbidden error
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        tables = pd.read_html(url, storage_options=headers)
        df = tables[0]
        df['Symbol'] = df['Symbol'].str.replace('.', '-')
        return df
    except Exception as e:
        st.error(f"Error loading S&P 500 list: {e}")
        return pd.DataFrame()

# --- Get Stock Data from Alpaca ---
def get_stock_data(symbol, days_back=200):
    """Fetch 30-min bar data from Alpaca"""
    try:
        client = get_alpaca_client()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame(30, "Min"),
            start=start_date,
            end=end_date
        )
        
        bars = client.get_stock_bars(request_params)
        df = bars.df
        
        if df.empty:
            return None
            
        df = df.reset_index()
        
        if 'close' not in df.columns:
            return None
            
        return df
        
    except Exception as e:
        return None

# --- Get Market Cap ---
def get_market_cap(symbol):
    """Get market cap - simplified version"""
    try:
        import yfinance as yf
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('marketCap', 0)
    except:
        return 0

# --- Calculate SMAs and Check Conditions ---
def check_sma_conditions(df, sma_short=65, sma_long=182, max_pct_short=5.0, 
                        max_pct_long=5.0, min_volume=0, sp500_info=None, 
                        sector_filter=None, min_market_cap=0, max_market_cap=float('inf')):
    """Check if stock meets all conditions including new filters"""
    # Convert days to 30-minute bars (13 bars per trading day)
    BARS_PER_DAY = 13
    sma_short_bars = sma_short * BARS_PER_DAY
    sma_long_bars = sma_long * BARS_PER_DAY
    
    if df is None or len(df) < sma_long_bars:
        return False, None
    
    # Calculate SMAs using converted bar counts
    df['SMA_65'] = df['close'].rolling(window=sma_short_bars).mean()
    df['SMA_182'] = df['close'].rolling(window=sma_long_bars).mean()
    
    # Get latest values
    latest = df.iloc[-1]
    current_price = latest['close']
    sma_65_value = latest['SMA_65']
    sma_182_value = latest['SMA_182']
    current_volume = latest['volume']
    
    # Check if SMAs are valid
    if pd.isna(sma_65_value) or pd.isna(sma_182_value):
        return False, None
    
    # Calculate percentage above SMAs
    pct_above_65 = ((current_price - sma_65_value) / sma_65_value) * 100
    pct_above_182 = ((current_price - sma_182_value) / sma_182_value) * 100
    
    # Basic SMA conditions
    above_both = current_price > sma_65_value and current_price > sma_182_value
    within_range_65 = 0 < pct_above_65 <= max_pct_short
    within_range_182 = 0 < pct_above_182 <= max_pct_long
    
    # Volume filter
    volume_ok = current_volume >= min_volume
    
    # Get sector and market cap if available
    sector = "N/A"
    market_cap = 0
    
    if sp500_info is not None:
        symbol_clean = latest.get('symbol', '').replace('-', '.')
        stock_info = sp500_info[sp500_info['Symbol'] == symbol_clean]
        if not stock_info.empty:
            sector = stock_info.iloc[0].get('GICS Sector', 'N/A')
            market_cap = get_market_cap(symbol_clean)
    
    # Sector filter
    sector_ok = True
    if sector_filter and sector_filter != "All Sectors":
        sector_ok = sector == sector_filter
    
    # Market cap filter
    market_cap_ok = min_market_cap <= market_cap <= max_market_cap
    
    meets_criteria = (above_both and within_range_65 and within_range_182 
                     and volume_ok and sector_ok and market_cap_ok)
    
    result = {
        'current_price': current_price,
        'sma_65': sma_65_value,
        'sma_182': sma_182_value,
        'pct_above_65': pct_above_65,
        'pct_above_182': pct_above_182,
        'volume': current_volume,
        'sector': sector,
        'market_cap': market_cap,
        'meets_criteria': meets_criteria,
        'df': df
    }
    
    return meets_criteria, result

# --- Email Functions ---
def save_email_settings(email, smtp_server, smtp_port, smtp_username, smtp_password, enabled):
    """Save email notification settings"""
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO email_settings 
                 (id, email, smtp_server, smtp_port, smtp_username, smtp_password, enabled)
                 VALUES (1, ?, ?, ?, ?, ?, ?)''',
              (email, smtp_server, smtp_port, smtp_username, smtp_password, enabled))
    conn.commit()

def get_email_settings():
    """Retrieve email settings"""
    c = conn.cursor()
    c.execute('SELECT * FROM email_settings WHERE id = 1')
    result = c.fetchone()
    if result:
        return {
            'email': result[1],
            'smtp_server': result[2],
            'smtp_port': result[3],
            'smtp_username': result[4],
            'smtp_password': result[5],
            'enabled': result[6]
        }
    return None

def send_email_notification(stocks_found, settings):
    """Send email with scan results"""
    if not settings or not settings['enabled']:
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"🎯 SMA Screener Alert: {len(stocks_found)} Stock(s) Found!"
        msg['From'] = settings['smtp_username']
        msg['To'] = settings['email']
        
        # Create HTML email with dark blue theme
        html = f"""
        <html>
          <head>
            <style>
              body {{
                font-family: 'Inter', Arial, sans-serif;
                background: linear-gradient(135deg, #0A2647 0%, #144272 100%);
                color: #FFFFFF;
                padding: 20px;
              }}
              .container {{
                max-width: 800px;
                margin: 0 auto;
                background: #1a1f3a;
                border-radius: 15px;
                padding: 30px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
              }}
              h2 {{
                color: #2C74B3;
                border-bottom: 3px solid #205295;
                padding-bottom: 10px;
              }}
              table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                border-radius: 10px;
                overflow: hidden;
              }}
              th {{
                background: linear-gradient(135deg, #205295 0%, #2C74B3 100%);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 700;
              }}
              td {{
                padding: 12px 15px;
                border-bottom: 1px solid #205295;
                background: #1a1f3a;
              }}
              tr:hover td {{
                background: #253557;
              }}
              .footer {{
                margin-top: 30px;
                text-align: center;
                color: #B8C5D6;
                font-size: 0.9rem;
              }}
              .badge {{
                display: inline-block;
                padding: 5px 10px;
                border-radius: 15px;
                font-weight: 600;
                font-size: 0.85rem;
              }}
              .badge-success {{
                background: #00D9A5;
                color: #0A2647;
              }}
            </style>
          </head>
          <body>
            <div class="container">
              <h2>📈 S&P 500 SMA Screener Results</h2>
              <p style="font-size: 1.1rem; color: #B8C5D6;">
                Found <span class="badge badge-success">{len(stocks_found)}</span> stocks meeting your criteria:
              </p>
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Company</th>
                    <th>Price</th>
                    <th>% Above SMA65</th>
                    <th>% Above SMA182</th>
                    <th>Sector</th>
                  </tr>
                </thead>
                <tbody>
        """
        
        for stock in stocks_found:
            html += f"""
                  <tr>
                    <td><strong>{stock['Symbol']}</strong></td>
                    <td>{stock['Company']}</td>
                    <td>${stock['Price']:.2f}</td>
                    <td>{stock['% Above SMA65']:.2f}%</td>
                    <td>{stock['% Above SMA182']:.2f}%</td>
                    <td>{stock['Sector']}</td>
                  </tr>
            """
        
        html += f"""
                </tbody>
              </table>
              <div class="footer">
                <p>Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Powered by S&P 500 SMA Screener Pro 🚀</p>
              </div>
            </div>
          </body>
        </html>
        """
        
        msg.attach(MIMEText(html, 'html'))
        
        # Send email
        with smtplib.SMTP(settings['smtp_server'], settings['smtp_port']) as server:
            server.starttls()
            server.login(settings['smtp_username'], settings['smtp_password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

# --- Favorites Functions ---
def add_to_favorites(symbol, company, notes=""):
    """Add stock to favorites"""
    try:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO favorites (symbol, company, added_date, notes)
                     VALUES (?, ?, ?, ?)''',
                  (symbol, company, datetime.now().strftime('%Y-%m-%d'), notes))
        conn.commit()
        return True
    except:
        return False

def remove_from_favorites(symbol):
    """Remove stock from favorites"""
    c = conn.cursor()
    c.execute('DELETE FROM favorites WHERE symbol = ?', (symbol,))
    conn.commit()

def get_favorites():
    """Get all favorite stocks"""
    c = conn.cursor()
    c.execute('SELECT * FROM favorites ORDER BY added_date DESC')
    results = c.fetchall()
    if results:
        return pd.DataFrame(results, columns=['Symbol', 'Company', 'Added Date', 'Notes'])
    return pd.DataFrame()

def is_favorite(symbol):
    """Check if stock is in favorites"""
    c = conn.cursor()
    c.execute('SELECT symbol FROM favorites WHERE symbol = ?', (symbol,))
    return c.fetchone() is not None

# --- Save Scan Results ---
def save_scan_results(stocks):
    """Save scan results to history"""
    c = conn.cursor()
    scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    for stock in stocks:
        c.execute('''INSERT INTO scan_history 
                     (scan_date, symbol, price, pct_above_65, pct_above_182, 
                      volume, market_cap, sector)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (scan_date, stock['Symbol'], stock['Price'], 
                   stock['% Above SMA65'], stock['% Above SMA182'],
                   stock.get('Volume', 0), stock.get('Market Cap', 0), 
                   stock.get('Sector', 'N/A')))
    conn.commit()

def get_scan_history(days=7):
    """Get scan history"""
    c = conn.cursor()
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    c.execute('''SELECT * FROM scan_history 
                 WHERE scan_date >= ? 
                 ORDER BY scan_date DESC''', (cutoff_date,))
    results = c.fetchall()
    if results:
        return pd.DataFrame(results, columns=['ID', 'Scan Date', 'Symbol', 'Price', 
                                              '% Above SMA65', '% Above SMA182',
                                              'Volume', 'Market Cap', 'Sector'])
    return pd.DataFrame()

# --- Scheduled Scan Functions ---
def save_schedule_settings(enabled, scan_time):
    """Save schedule settings"""
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO scan_schedule (id, enabled, scan_time, last_run)
                 VALUES (1, ?, ?, ?)''',
              (enabled, scan_time, ''))
    conn.commit()

def get_schedule_settings():
    """Get schedule settings"""
    c = conn.cursor()
    c.execute('SELECT * FROM scan_schedule WHERE id = 1')
    result = c.fetchone()
    if result:
        return {
            'enabled': result[1],
            'scan_time': result[2],
            'last_run': result[3]
        }
    return {'enabled': 0, 'scan_time': '09:00', 'last_run': ''}

# --- Create Chart with Dark Blue Theme ---
def create_chart(symbol, result_data):
    """Create interactive chart with price and SMAs"""
    df = result_data['df']
    df_chart = df.tail(100).copy()
    
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'{symbol} - Price & SMAs', 'Volume'),
        row_heights=[0.7, 0.3]
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df_chart['timestamp'],
            open=df_chart['open'],
            high=df_chart['high'],
            low=df_chart['low'],
            close=df_chart['close'],
            name='Price',
            increasing_line_color='#00D9A5',
            decreasing_line_color='#FF6B6B'
        ),
        row=1, col=1
    )
    
    # SMA 65
    fig.add_trace(
        go.Scatter(
            x=df_chart['timestamp'],
            y=df_chart['SMA_65'],
            mode='lines',
            name='SMA 65',
            line=dict(color='#2C74B3', width=2)
        ),
        row=1, col=1
    )
    
    # SMA 182
    fig.add_trace(
        go.Scatter(
            x=df_chart['timestamp'],
            y=df_chart['SMA_182'],
            mode='lines',
            name='SMA 182',
            line=dict(color='#FFB800', width=2)
        ),
        row=1, col=1
    )
    
    # Volume
    colors = ['#00D9A5' if row['close'] >= row['open'] else '#FF6B6B' 
              for idx, row in df_chart.iterrows()]
    
    fig.add_trace(
        go.Bar(
            x=df_chart['timestamp'],
            y=df_chart['volume'],
            name='Volume',
            marker_color=colors,
            opacity=0.7
        ),
        row=2, col=1
    )
    
    # Update layout with dark blue theme
    fig.update_layout(
        height=600,
        showlegend=True,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        plot_bgcolor='#0A2647',
        paper_bgcolor='#1a1f3a',
        font=dict(color='#FFFFFF', family='Inter'),
        legend=dict(
            bgcolor='#144272',
            bordercolor='#205295',
            borderwidth=2
        )
    )
    
    fig.update_xaxes(
        title_text="Date", 
        row=2, col=1,
        gridcolor='#205295',
        showgrid=True
    )
    fig.update_yaxes(
        title_text="Price ($)", 
        row=1, col=1,
        gridcolor='#205295',
        showgrid=True
    )
    fig.update_yaxes(
        title_text="Volume", 
        row=2, col=1,
        gridcolor='#205295',
        showgrid=True
    )
    
    return fig

# --- Main App ---
def main():
    # Load custom CSS
    load_custom_css()
    
    # Display logo and header
    display_logo_header()
    
    # Create tabs with icons
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Scanner", 
        "⭐ Favorites", 
        "📧 Notifications", 
        "⏰ Schedule",
        "📊 History"
    ])
    
    # --- TAB 1: SCANNER ---
    with tab1:
        # Sidebar - Settings
        with st.sidebar:
            st.markdown("### ⚙️ Scanner Settings")
            st.markdown("---")
            
            st.markdown("#### 📐 SMA Parameters")
            sma_short = st.number_input("Short SMA Period", min_value=1, max_value=200, value=65)
            sma_long = st.number_input("Long SMA Period", min_value=1, max_value=500, value=182)
            
            st.markdown("---")
            st.markdown("#### 📏 Distance from SMAs")
            max_pct_sma65 = st.slider("Max % Above SMA 65", 0.5, 20.0, 5.0, 0.5)
            max_pct_sma182 = st.slider("Max % Above SMA 182", 0.5, 20.0, 5.0, 0.5)
            
            st.markdown("---")
            st.markdown("#### 📊 Additional Filters")
            
            # Volume filter
            min_volume = st.number_input(
                "Min Volume (0 = no filter)",
                min_value=0,
                value=0,
                step=100000,
                help="Minimum trading volume"
            )
            
            # Market cap filter
            market_cap_options = {
                "All Caps": (0, float('inf')),
                "Mega Cap (>$200B)": (200_000_000_000, float('inf')),
                "Large Cap ($10B-$200B)": (10_000_000_000, 200_000_000_000),
                "Mid Cap ($2B-$10B)": (2_000_000_000, 10_000_000_000),
                "Small Cap (<$2B)": (0, 2_000_000_000)
            }
            
            market_cap_choice = st.selectbox(
                "Market Cap Filter",
                options=list(market_cap_options.keys())
            )
            min_market_cap, max_market_cap = market_cap_options[market_cap_choice]
            
            # Load SP500 data for sector filter
            sp500_df = load_sp500_symbols()
            sectors = ["All Sectors"] + sorted(sp500_df['GICS Sector'].unique().tolist()) if not sp500_df.empty else ["All Sectors"]
            
            sector_filter = st.selectbox("Sector Filter", options=sectors)
            
            st.markdown("---")
            st.markdown("#### 🎯 Scanning Options")
            max_stocks_to_scan = st.number_input(
                "Max Stocks to Scan",
                min_value=10,
                max_value=500,
                value=100,
                step=10
            )
            
            st.markdown("---")
            scan_button = st.button("🔍 Start Scan", type="primary", use_container_width=True)
        
        # Main scanning area
        if scan_button:
            # Clear any previous results first
            scan_container = st.container()
            
            with scan_container:
                st.markdown(f"""
                    <div class="custom-card">
                        <h3>🔄 Scanning in Progress...</h3>
                        <p>Analyzing up to {max_stocks_to_scan} S&P 500 stocks with your criteria</p>
                        <p style="color: var(--text-gray); font-size: 0.9rem; margin-top: 10px;">
                            ⏱️ This may take a few minutes depending on the number of stocks and data range
                        </p>
                    </div>
                """, unsafe_allow_html=True)
                
                if sp500_df.empty:
                    st.error("❌ Failed to load S&P 500 symbols")
                    st.stop()
                
                symbols_to_scan = sp500_df['Symbol'].head(max_stocks_to_scan).tolist()
                
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()
                stats_placeholder = st.empty()
                
                qualifying_stocks = []
                scanned_count = 0
                
                for idx, symbol in enumerate(symbols_to_scan):
                    scanned_count += 1
                    
                    # Update status with more detailed information
                    status_text.markdown(f"""
                        <div style="text-align: center; color: var(--text-gray); padding: 10px;">
                            <div style="font-size: 1.2rem; margin-bottom: 5px;">
                                Scanning <span style="color: var(--light-blue); font-weight: 700;">{symbol}</span>
                            </div>
                            <div style="font-size: 0.9rem;">
                                Progress: {idx + 1} of {len(symbols_to_scan)} stocks 
                                | Found: <span style="color: var(--success-green); font-weight: 600;">{len(qualifying_stocks)}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    progress_bar.progress((idx + 1) / len(symbols_to_scan))
                    
                    # Fetch and analyze stock data
                    df = get_stock_data(symbol)
                    
                    if df is not None:
                        stock_info = sp500_df[sp500_df['Symbol'] == symbol]
                        
                        meets_criteria, result = check_sma_conditions(
                            df, sma_short, sma_long, max_pct_sma65, max_pct_sma182,
                            min_volume, sp500_df, 
                            None if sector_filter == "All Sectors" else sector_filter,
                            min_market_cap, max_market_cap
                        )
                        
                        if meets_criteria:
                            company_name = stock_info['Security'].values[0] if not stock_info.empty else "N/A"
                            
                            qualifying_stocks.append({
                                'Symbol': symbol,
                                'Company': company_name,
                                'Price': result['current_price'],
                                'SMA 65': result['sma_65'],
                                'SMA 182': result['sma_182'],
                                '% Above SMA65': result['pct_above_65'],
                                '% Above SMA182': result['pct_above_182'],
                                'Volume': result['volume'],
                                'Market Cap': result['market_cap'],
                                'Sector': result['sector'],
                                'result_data': result
                            })
                
                # Clear progress indicators after scan completes
                progress_bar.empty()
                status_text.empty()
            
            # Save results
            if qualifying_stocks:
                save_scan_results(qualifying_stocks)
            
            # Send email notification
            email_settings = get_email_settings()
            if email_settings and email_settings['enabled'] and qualifying_stocks:
                if send_email_notification(qualifying_stocks, email_settings):
                    st.success("📧 Email notification sent successfully!")
            
            # Display Results
            st.markdown("---")
            
            if qualifying_stocks:
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(create_metric_card(
                        "Stocks Found",
                        len(qualifying_stocks),
                        icon="✅"
                    ), unsafe_allow_html=True)
                
                with col2:
                    avg_price = np.mean([s['Price'] for s in qualifying_stocks])
                    st.markdown(create_metric_card(
                        "Avg Price",
                        f"${avg_price:.2f}",
                        icon="💰"
                    ), unsafe_allow_html=True)
                
                with col3:
                    avg_sma65 = np.mean([s['% Above SMA65'] for s in qualifying_stocks])
                    st.markdown(create_metric_card(
                        "Avg % Above SMA65",
                        f"{avg_sma65:.2f}%",
                        icon="📈"
                    ), unsafe_allow_html=True)
                
                with col4:
                    total_vol = sum([s['Volume'] for s in qualifying_stocks])
                    st.markdown(create_metric_card(
                        "Total Volume",
                        f"{total_vol/1e6:.1f}M",
                        icon="📊"
                    ), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                results_df = pd.DataFrame(qualifying_stocks)
                
                # Display table
                st.markdown("### 📋 Results Table")
                display_df = results_df.drop(columns=['result_data']).copy()
                display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
                display_df['SMA 65'] = display_df['SMA 65'].apply(lambda x: f"${x:.2f}")
                display_df['SMA 182'] = display_df['SMA 182'].apply(lambda x: f"${x:.2f}")
                display_df['% Above SMA65'] = display_df['% Above SMA65'].apply(lambda x: f"{x:.2f}%")
                display_df['% Above SMA182'] = display_df['% Above SMA182'].apply(lambda x: f"{x:.2f}%")
                display_df['Volume'] = display_df['Volume'].apply(lambda x: f"{x:,.0f}")
                display_df['Market Cap'] = display_df['Market Cap'].apply(
                    lambda x: f"${x/1e9:.2f}B" if x > 0 else "N/A"
                )
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"sma_screener_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=False
                )
                
                # Detailed view
                st.markdown("---")
                st.markdown("### 📈 Detailed Stock Analysis")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_symbol = st.selectbox(
                        "Select a stock to view details:",
                        options=[stock['Symbol'] for stock in qualifying_stocks],
                        key="stock_selector"
                    )
                
                with col2:
                    if selected_symbol:
                        stock_data = next(s for s in qualifying_stocks if s['Symbol'] == selected_symbol)
                        
                        # Add to favorites button
                        if is_favorite(selected_symbol):
                            if st.button("💔 Remove from Favorites", use_container_width=True):
                                remove_from_favorites(selected_symbol)
                                st.success(f"✅ Removed {selected_symbol} from favorites")
                                st.rerun()
                        else:
                            if st.button("⭐ Add to Favorites", use_container_width=True):
                                add_to_favorites(selected_symbol, stock_data['Company'])
                                st.success(f"✅ Added {selected_symbol} to favorites!")
                                st.rerun()
                
                if selected_symbol:
                    stock_data = next(s for s in qualifying_stocks if s['Symbol'] == selected_symbol)
                    
                    # Display metrics
                    st.markdown("<br>", unsafe_allow_html=True)
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        st.markdown(create_metric_card(
                            "Current Price",
                            f"${stock_data['Price']:.2f}",
                            icon="💵"
                        ), unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(create_metric_card(
                            "SMA 65",
                            f"${stock_data['SMA 65']:.2f}",
                            icon="📊"
                        ), unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(create_metric_card(
                            "SMA 182",
                            f"${stock_data['SMA 182']:.2f}",
                            icon="📈"
                        ), unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(create_metric_card(
                            "Volume",
                            f"{stock_data['Volume']/1e6:.2f}M",
                            icon="📊"
                        ), unsafe_allow_html=True)
                    
                    with col5:
                        market_cap_display = f"${stock_data['Market Cap']/1e9:.2f}B" if stock_data['Market Cap'] > 0 else "N/A"
                        st.markdown(create_metric_card(
                            "Market Cap",
                            market_cap_display,
                            icon="🏢"
                        ), unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # Display chart
                    fig = create_chart(selected_symbol, stock_data['result_data'])
                    st.plotly_chart(fig, use_container_width=True)
                    
            else:
                st.markdown("""
                    <div class="custom-card" style="text-align: center; padding: 40px;">
                        <h2>❌ No Stocks Found</h2>
                        <p style="color: var(--text-gray); font-size: 1.1rem;">
                            Try adjusting your filter parameters to find more opportunities
                        </p>
                    </div>
                """, unsafe_allow_html=True)
        
        else:
            # Welcome screen
            st.markdown("""
                <div class="custom-card">
                    <h2>👋 Welcome to S&P 500 SMA Screener Pro</h2>
                    <p style="color: var(--text-gray); font-size: 1.1rem; line-height: 1.6;">
                        Your professional-grade stock screening tool powered by real-time Alpaca market data.
                    </p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="custom-card">
                        <h3>🎯 New Features</h3>
                        <ul style="color: var(--text-gray); line-height: 2;">
                            <li><strong>Volume Filter:</strong> Set minimum trading volume</li>
                            <li><strong>Market Cap Filter:</strong> Focus on large, mid, or small caps</li>
                            <li><strong>Sector Filter:</strong> Scan specific sectors only</li>
                            <li><strong>Favorites System:</strong> Save stocks for quick access</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="custom-card">
                        <h3>🚀 Advanced Capabilities</h3>
                        <ul style="color: var(--text-gray); line-height: 2;">
                            <li><strong>Email Alerts:</strong> Get notified of new opportunities</li>
                            <li><strong>Scheduled Scans:</strong> Automate daily screening</li>
                            <li><strong>History Tracking:</strong> Review past scan results</li>
                            <li><strong>Professional Charts:</strong> Interactive Plotly visualizations</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="custom-card" style="text-align: center; margin-top: 20px;">
                    <h3>📝 Quick Start Guide</h3>
                    <p style="color: var(--text-gray); font-size: 1.05rem; line-height: 1.8;">
                        1. Adjust your SMA parameters in the sidebar<br>
                        2. Set your distance tolerance from the SMAs<br>
                        3. Apply additional filters (volume, sector, market cap)<br>
                        4. Click <strong style="color: var(--success-green);">"Start Scan"</strong> to find opportunities<br>
                        5. Review results and add favorites for tracking
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # --- TAB 2: FAVORITES ---
    with tab2:
        st.markdown("## ⭐ Your Favorite Stocks")
        
        favorites_df = get_favorites()
        
        if not favorites_df.empty:
            st.markdown(f"""
                <div class="custom-card">
                    <h3>📌 You have {len(favorites_df)} favorite stocks</h3>
                </div>
            """, unsafe_allow_html=True)
            
            st.dataframe(favorites_df, use_container_width=True, hide_index=True)
            
            # Remove from favorites
            st.markdown("---")
            col1, col2 = st.columns([3, 1])
            with col1:
                symbol_to_remove = st.selectbox(
                    "Select stock to remove:",
                    options=favorites_df['Symbol'].tolist(),
                    key="remove_fav"
                )
            with col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Remove", use_container_width=True):
                    remove_from_favorites(symbol_to_remove)
                    st.success(f"✅ Removed {symbol_to_remove}")
                    st.rerun()
        else:
            st.markdown("""
                <div class="custom-card" style="text-align: center; padding: 60px;">
                    <h2>📭 No Favorites Yet</h2>
                    <p style="color: var(--text-gray); font-size: 1.2rem;">
                        Add stocks from the Scanner tab to start tracking them!
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # --- TAB 3: EMAIL NOTIFICATIONS ---
    with tab3:
        st.markdown("## 📧 Email Notification Settings")
        
        current_settings = get_email_settings()
        
        with st.form("email_settings_form"):
            st.markdown("### 🔧 SMTP Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                email = st.text_input(
                    "📮 Your Email Address",
                    value=current_settings['email'] if current_settings else ""
                )
                smtp_server = st.text_input(
                    "🌐 SMTP Server",
                    value=current_settings['smtp_server'] if current_settings else "smtp.gmail.com",
                    help="e.g., smtp.gmail.com for Gmail"
                )
                smtp_username = st.text_input(
                    "👤 SMTP Username",
                    value=current_settings['smtp_username'] if current_settings else "",
                    help="Usually your email address"
                )
            
            with col2:
                smtp_port = st.number_input(
                    "🔌 SMTP Port",
                    value=current_settings['smtp_port'] if current_settings else 587,
                    help="Usually 587 for TLS"
                )
                smtp_password = st.text_input(
                    "🔐 SMTP Password",
                    type="password",
                    help="Use App Password for Gmail"
                )
                enabled = st.checkbox(
                    "✅ Enable Email Notifications",
                    value=current_settings['enabled'] if current_settings else False
                )
            
            st.markdown("""
                <div class="custom-card">
                    <h4>📝 Gmail Setup Instructions</h4>
                    <ol style="color: var(--text-gray); line-height: 1.8;">
                        <li>Enable 2-factor authentication on your Google account</li>
                        <li>Go to: <a href="https://myaccount.google.com/apppasswords" target="_blank" 
                            style="color: var(--light-blue);">https://myaccount.google.com/apppasswords</a></li>
                        <li>Create an app password for "Mail"</li>
                        <li>Use that 16-character password here (not your regular Gmail password)</li>
                    </ol>
                    
                    <h4 style="margin-top: 20px;">🌐 Common SMTP Servers</h4>
                    <ul style="color: var(--text-gray); line-height: 1.8;">
                        <li><strong>Gmail:</strong> smtp.gmail.com (port 587)</li>
                        <li><strong>Outlook:</strong> smtp-mail.outlook.com (port 587)</li>
                        <li><strong>Yahoo:</strong> smtp.mail.yahoo.com (port 587)</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
            
            submitted = st.form_submit_button("💾 Save Settings", use_container_width=True, type="primary")
            
            if submitted:
                save_email_settings(email, smtp_server, smtp_port, smtp_username, smtp_password, 1 if enabled else 0)
                st.success("✅ Email settings saved successfully!")
    
    # --- TAB 4: SCHEDULE ---
    with tab4:
        st.markdown("## ⏰ Automated Scan Schedule")
        
        schedule_settings = get_schedule_settings()
        
        st.markdown("""
            <div class="custom-card">
                <p style="color: var(--text-gray); font-size: 1.05rem;">
                    <strong>Note:</strong> Automated scheduling requires the app to run continuously. 
                    For production use, consider deploying to a cloud service or using a task scheduler.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("schedule_form"):
            enabled = st.checkbox(
                "✅ Enable Scheduled Scans",
                value=schedule_settings['enabled']
            )
            
            scan_time = st.time_input(
                "🕐 Daily Scan Time",
                value=datetime.strptime(schedule_settings['scan_time'], '%H:%M').time() 
                      if schedule_settings['scan_time'] else datetime.strptime('09:00', '%H:%M').time()
            )
            
            if schedule_settings['last_run']:
                st.info(f"Last scan run: {schedule_settings['last_run']}")
            
            submitted = st.form_submit_button("💾 Save Schedule", use_container_width=True, type="primary")
            
            if submitted:
                save_schedule_settings(1 if enabled else 0, scan_time.strftime('%H:%M'))
                st.success("✅ Schedule settings saved!")
        
        st.markdown("""
            <div class="custom-card">
                <h3>🚀 Deployment Options for Automated Scans</h3>
                
                <h4>1. Streamlit Cloud (Recommended for Beginners)</h4>
                <p style="color: var(--text-gray);">Deploy your app for free with automatic scheduling support</p>
                
                <h4>2. Heroku</h4>
                <p style="color: var(--text-gray);">Use with scheduler add-on for production-grade automation</p>
                
                <h4>3. Local Cron Job</h4>
                <p style="color: var(--text-gray);">Run on your computer with Task Scheduler (Windows) or cron (Mac/Linux)</p>
                
                <h4>4. Cloud Functions</h4>
                <p style="color: var(--text-gray);">AWS Lambda, Google Cloud Functions for serverless execution</p>
            </div>
        """, unsafe_allow_html=True)
    
    # --- TAB 5: HISTORY ---
    with tab5:
        st.markdown("## 📊 Scan History & Analytics")
        
        days_back = st.slider("Show history for last N days:", 1, 30, 7)
        
        history_df = get_scan_history(days_back)
        
        if not history_df.empty:
            # Analytics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(create_metric_card(
                    "Total Scans",
                    len(history_df['Scan Date'].unique()),
                    icon="🔍"
                ), unsafe_allow_html=True)
            
            with col2:
                st.markdown(create_metric_card(
                    "Unique Stocks",
                    len(history_df['Symbol'].unique()),
                    icon="📈"
                ), unsafe_allow_html=True)
            
            with col3:
                most_common = history_df['Symbol'].mode()[0] if not history_df.empty else "N/A"
                st.markdown(create_metric_card(
                    "Most Common",
                    most_common,
                    icon="⭐"
                ), unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            
            # Download history
            csv = history_df.to_csv(index=False)
            st.download_button(
                label="📥 Download History as CSV",
                data=csv,
                file_name=f"scan_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.markdown("""
                <div class="custom-card" style="text-align: center; padding: 60px;">
                    <h2>📭 No History Available</h2>
                    <p style="color: var(--text-gray); font-size: 1.2rem;">
                        Run your first scan to start building your history!
                    </p>
                </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
        <div style="text-align: center; color: var(--text-gray); padding: 20px;">
            <p>Made with ❤️ using Streamlit & Alpaca API</p>
            <p style="font-size: 0.9rem;">S&P 500 SMA Screener Pro © 2024</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
