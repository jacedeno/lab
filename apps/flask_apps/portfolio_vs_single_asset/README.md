 # Portfolio vs Single Asset Comparison Tool

A professional Flask web application for comparing investment portfolio performance against index funds or individual stocks.

## 🐛 Bug Fixes Applied

### Critical Calculation Bug Fixed
The original Streamlit application had a **major calculation error** that was causing inflated portfolio values:

**Problem:** The simulation functions were missing the initial portfolio value in their results. The functions started the portfolio values list from index 1 instead of index 0, which meant:
- The initial investment value was not included in the results
- The data length didn't match the date index
- This caused incorrect calculations and displayed values

**Solution:** 
- Modified `simulate_portfolio()` to include the initial portfolio value at index 0
- Modified `simulate_index_investment()` to include the initial portfolio value at index 0
- Added tracking of total invested amount throughout the simulation
- Now correctly displays profit/loss and return percentages

### Example of the Fix
**Before (Buggy):**
```python
portfolio_values = []
for i in range(1, len(periods)):  # Started from 1, missing initial value
    # ... calculations ...
    portfolio_values.append(value)
return pd.DataFrame({'Portfolio Value': portfolio_values}, index=periods[1:])
```

**After (Fixed):**
```python
portfolio_values = [initial_portfolio_value]  # Include initial value
total_invested_list = [initial_investment]
for i in range(1, len(periods)):
    # ... calculations ...
    total_invested += contribution
    portfolio_values.append(value)
    total_invested_list.append(total_invested)
return pd.DataFrame({
    'Portfolio Value': portfolio_values,
    'Total Invested': total_invested_list
}, index=periods)
```

## ✨ Improvements Made

### 1. **Streamlit App (portfolio_vs_single.py)**
- ✅ Fixed calculation functions
- ✅ Removed "Annually" option - now only Weekly and Monthly
- ✅ Added total invested tracking
- ✅ Improved metrics display with profit/loss and return percentages

### 2. **New Flask Web Application (app.py)**
- ✅ Modern, professional web interface
- ✅ Interactive Plotly charts (instead of static matplotlib)
- ✅ Real-time calculations via AJAX
- ✅ Responsive design with Tailwind CSS
- ✅ Beautiful gradient theme
- ✅ Loading states and error handling
- ✅ Mobile-friendly interface

### 3. **Features**
- Dollar-cost averaging simulation
- Whole-share purchase modeling
- Cash carryover between periods
- Side-by-side comparison of portfolio vs index
- Visual profit/loss indicators
- Total return percentage calculations

## 🚀 Installation & Usage

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Setup

1. **Navigate to the project directory:**
```bash
cd /root/flask_apps/portfolio_vs_single_asset
```

2. **Activate virtual environment (already created):**
```bash
source venv/bin/activate
```

3. **Install dependencies (already installed):**
```bash
pip install -r requirements.txt
```

### Running the Flask App

```bash
python app.py
```

The application will be available at:
- Local: http://127.0.0.1:5000
- Network: http://192.168.68.81:5000

### Running the Streamlit App

```bash
streamlit run portfolio_vs_single.py
```

## 📊 How It Works

### Investment Simulation Logic

1. **Initial Investment:**
   - Divided equally among selected stocks (or fully for index)
   - Purchases maximum whole shares possible
   - Carries over remaining cash

2. **Periodic Contributions:**
   - Fixed amount added each period (weekly or monthly)
   - Combined with leftover cash from previous period
   - Purchases whole shares only
   - New leftover cash carried to next period

3. **Portfolio Valuation:**
   - Current value = Total Shares × Current Price
   - Tracked at each period
   - Compared against total amount invested

### Example Calculation

**Scenario:** $1,000 initial + $200/week for 6 years in SPY

- Week 1: Buy shares with $1,000 → e.g., 2 shares @ $450 = $900, leftover $100
- Week 2: $200 + $100 = $300 → buy 0 shares @ $455, leftover $300
- Week 3: $200 + $300 = $500 → buy 1 share @ $460, leftover $40
- Continue for ~312 weeks...
- Final value = accumulated shares × current price

**Realistic Results for SPY (6 years, 2019-2025):**
- Total Invested: ~$63,400
- Final Value: ~$90,000-120,000 (depending on exact dates)
- Return: ~40-90%

## 🎨 Flask App Features

### User Interface
- **Clean, modern design** with gradient header
- **Professional cards** with shadow effects
- **Interactive charts** with Plotly (zoom, pan, hover)
- **Responsive layout** works on all devices
- **Real-time validation** and error messages

### Technical Features
- **AJAX-based** calculations (no page reload)
- **Loading states** with spinner
- **Error handling** with user-friendly messages
- **Professional color coding** for profits (green) vs losses (red)
- **Formatted currency** and percentage displays

## 📝 Input Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| Stock Tickers | Comma-separated ticker symbols | AAPL, MSFT, GOOGL |
| Comparison Index | Single ticker to compare against | SPY, QQQ |
| Start Date | Beginning of investment period | 2019-01-01 |
| End Date | End of investment period | 2025-01-01 |
| Initial Investment | One-time initial amount | $1,000 |
| Regular Contribution | Amount added each period | $200 |
| Frequency | Weekly or Monthly | Weekly |

## 🔧 Technology Stack

### Backend
- **Flask** - Web framework
- **yfinance** - Stock data API
- **pandas** - Data manipulation
- **numpy** - Numerical calculations
- **Plotly** - Interactive charts

### Frontend
- **Tailwind CSS** - Styling framework
- **Plotly.js** - Chart rendering
- **Vanilla JavaScript** - Interactivity
- **Inter Font** - Professional typography

## ⚠️ Disclaimer

This tool is for **educational and informational purposes only**. It is NOT financial advice and should not be considered as a recommendation to buy or sell any securities. 

- Past performance does not guarantee future results
- All investments carry risk
- Always conduct your own research
- Consult with a qualified financial advisor before making investment decisions

## 👨‍💻 Created By

**Jose Cedeno**

---

## 📄 Files Structure

```
portfolio_vs_single_asset/
├── app.py                      # Flask application
├── portfolio_vs_single.py      # Fixed Streamlit app
├── fixed_calculations.py       # Corrected calculation functions
├── test_calculations.py        # Test script
├── templates/
│   └── index.html             # Flask web interface
├── static/                    # (Reserved for custom CSS/JS)
├── assets/                    # Logo and favicon
├── venv/                      # Virtual environment
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🔍 Testing the Fix

To verify the calculations are now correct, you can run:

```bash
python test_calculations.py
```

This will compare the buggy vs fixed versions and show the difference in results.
