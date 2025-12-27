"""
Portfolio vs Single Asset Comparison - Flask Application
Professional web app for comparing investment portfolios
"""
from flask import Flask, render_template, request, jsonify
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objs as go
import plotly.utils
import json
import random
from typing import Dict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'portfolio-comparison-app-2025'


def download_data(tickers, start, end, interval):
    """Downloads stock data from Yahoo Finance."""
    try:
        is_single = isinstance(tickers, str)
        if is_single:
            tickers = [tickers]
        
        data = yf.download(tickers, start=start, end=end, interval=interval, 
                          auto_adjust=True, progress=False)
        
        if data.empty:
            return pd.DataFrame() if not is_single else pd.Series()
        
        close_data = data['Close']
        
        if is_single and isinstance(close_data, pd.DataFrame):
            close_data = close_data.iloc[:, 0]
        
        return close_data
    except Exception as e:
        print(f"Error downloading data: {e}")
        return pd.DataFrame() if not isinstance(tickers, str) else pd.Series()


def generate_mock_data(ticker, start_date, end_date, interval):
    """Generate realistic mock stock data with visible monthly variations."""
    # Always use monthly data for better visualization
    periods = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Base prices and growth characteristics
    stock_profiles = {
        'SPY': {'base': 280, 'annual_growth': 0.12, 'volatility': 0.04},
        'QQQ': {'base': 180, 'annual_growth': 0.18, 'volatility': 0.05},
        'AAPL': {'base': 40, 'annual_growth': 0.25, 'volatility': 0.06},
        'MSFT': {'base': 120, 'annual_growth': 0.28, 'volatility': 0.05},
        'GOOGL': {'base': 55, 'annual_growth': 0.20, 'volatility': 0.055},
        'AMZN': {'base': 90, 'annual_growth': 0.15, 'volatility': 0.065},
        'NVDA': {'base': 40, 'annual_growth': 0.85, 'volatility': 0.12},
        'META': {'base': 140, 'annual_growth': 0.30, 'volatility': 0.08},
        'TSLA': {'base': 60, 'annual_growth': 0.45, 'volatility': 0.15},
        'BRK-B': {'base': 200, 'annual_growth': 0.10, 'volatility': 0.03},
        'JPM': {'base': 110, 'annual_growth': 0.08, 'volatility': 0.04},
        'FXAIX': {'base': 100, 'annual_growth': 0.12, 'volatility': 0.04}
    }
    
    profile = stock_profiles.get(ticker, {'base': 100, 'annual_growth': 0.10, 'volatility': 0.05})
    
    # Monthly growth rate with higher volatility for visible variation
    monthly_growth = profile['annual_growth'] / 12
    monthly_volatility = profile['volatility']
    
    # Generate price series with realistic monthly variations
    prices = [profile['base']]
    random.seed(hash(ticker) % 1000)  # Consistent randomness per ticker
    
    for i in range(1, len(periods)):
        # Add monthly trend plus volatility
        change_pct = random.gauss(monthly_growth, monthly_volatility)
        new_price = prices[-1] * (1 + change_pct)
        # Floor at 20% of base
        prices.append(max(new_price, profile['base'] * 0.2))
    
    return pd.Series(prices, index=periods)


def simulate_portfolio(stock_prices: pd.DataFrame, contribution: float, 
                      initial_investment: float) -> pd.DataFrame:
    """Simulates portfolio growth over time."""
    if isinstance(stock_prices, pd.Series):
        stock_prices = stock_prices.to_frame()
    
    periods = stock_prices.index
    num_tickers = len(stock_prices.columns)
    period_contribution = contribution / num_tickers
    
    shares_bought: Dict[str, np.ndarray] = {
        ticker: np.zeros(len(stock_prices)) for ticker in stock_prices.columns
    }
    leftover_cash: Dict[str, float] = {ticker: 0.0 for ticker in stock_prices.columns}
    initial_per_stock = initial_investment / num_tickers
    
    total_invested = initial_investment
    total_invested_list = [total_invested]
    
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


def simulate_index_investment(index_prices: pd.Series, contribution: float, 
                              initial_investment: float) -> pd.DataFrame:
    """Simulates index investment growth over time."""
    if isinstance(index_prices, pd.DataFrame):
        index_prices = index_prices.iloc[:, 0]
    
    periods = index_prices.index
    shares_bought = np.zeros(len(index_prices))
    leftover_cash = 0.0
    
    total_invested = initial_investment
    total_invested_list = [total_invested]
    
    price_initial = index_prices.iloc[0]
    initial_shares = initial_investment // price_initial
    leftover_cash = initial_investment % price_initial
    shares_bought[0] = initial_shares
    
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


@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Process the portfolio calculation request."""
    try:
        data = request.json
        
        tickers = [t.strip().upper() for t in data['tickers'].split(',') if t.strip()]
        index_ticker = data['indexTicker'].strip().upper()
        start_date = datetime.strptime(data['startDate'], '%Y-%m-%d')
        end_date = datetime.strptime(data['endDate'], '%Y-%m-%d')
        initial_investment = float(data['initialInvestment'])
        contribution = float(data['contribution'])
        frequency = data['frequency']
        
        if not tickers:
            return jsonify({'error': 'Please provide at least one ticker symbol'}), 400
        
        if start_date >= end_date:
            return jsonify({'error': 'Start date must be before end date'}), 400
        
        if end_date > datetime.now():
            return jsonify({'error': 'End date cannot be in the future'}), 400
        
        interval = '1wk' if frequency == 'Weekly' else '1mo'
        
        # Try real data first, fall back to mock if it fails
        stock_prices = download_data(tickers, start_date, end_date, interval)
        index_prices = download_data(index_ticker, start_date, end_date, interval)
        
        if stock_prices.empty or index_prices.empty:
            print("Real data unavailable, using mock data with monthly frequency")
            # Always use monthly for mock data for better visualization
            if len(tickers) == 1:
                stock_prices = generate_mock_data(tickers[0], start_date, end_date, '1mo')
            else:
                stock_data = {ticker: generate_mock_data(ticker, start_date, end_date, '1mo') 
                             for ticker in tickers}
                stock_prices = pd.DataFrame(stock_data)
            index_prices = generate_mock_data(index_ticker, start_date, end_date, '1mo')
            # Adjust contribution to monthly if using weekly frequency
            if frequency == 'Weekly':
                contribution = contribution * 4.33  # Convert weekly to monthly
        
        portfolio_df = simulate_portfolio(stock_prices, contribution, initial_investment)
        index_df = simulate_index_investment(index_prices, contribution, initial_investment)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=portfolio_df.index,
            y=portfolio_df['Portfolio Value'],
            mode='lines',
            name='Selected Stocks Portfolio',
            line=dict(color='#3b82f6', width=3),
            hovertemplate='<b>Date:</b> %{x}<br><b>Value:</b> $%{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=index_df.index,
            y=index_df['Index Value'],
            mode='lines',
            name=f'{index_ticker}',
            line=dict(color='#10b981', width=3),
            hovertemplate='<b>Date:</b> %{x}<br><b>Value:</b> $%{y:,.2f}<extra></extra>'
        ))
        
        fig.add_trace(go.Scatter(
            x=portfolio_df.index,
            y=portfolio_df['Total Invested'],
            mode='lines',
            name='Total Invested',
            line=dict(color='#94a3b8', width=2, dash='dash'),
            hovertemplate='<b>Date:</b> %{x}<br><b>Invested:</b> $%{y:,.2f}<extra></extra>'
        ))
        
        final_portfolio = portfolio_df['Portfolio Value'].iloc[-1]
        final_index = index_df['Index Value'].iloc[-1]
        total_invested = portfolio_df['Total Invested'].iloc[-1]
        
        portfolio_return = ((final_portfolio / total_invested) - 1) * 100
        index_return = ((final_index / total_invested) - 1) * 100
        
        fig.update_layout(
            title={'text': f'Portfolio Performance: Portfolio +{portfolio_return:.1f}% vs {index_ticker} +{index_return:.1f}%', 'font': {'size': 20, 'color': '#1e293b'}},
            xaxis={'title': 'Date', 'gridcolor': '#e2e8f0', 'showgrid': True, 'dtick': 'M1'},
            yaxis={'title': 'Portfolio Value (USD)', 'gridcolor': '#e2e8f0', 'showgrid': True, 'tickformat': '$,.0f'},
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            font={'family': 'Inter, sans-serif', 'size': 12},
            legend={'orientation': 'h', 'yanchor': 'bottom', 'y': 1.02, 'xanchor': 'center', 'x': 0.5, 'font': {'size': 14}},
            height=600,
            margin={'l': 60, 'r': 40, 't': 80, 'b': 60}
        )
        
        response = {
            'chart': json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder),
            'results': {
                'portfolio': {
                    'finalValue': final_portfolio,
                    'totalInvested': total_invested,
                    'profit': final_portfolio - total_invested,
                    'return': portfolio_return
                },
                'index': {
                    'name': index_ticker,
                    'finalValue': final_index,
                    'totalInvested': total_invested,
                    'profit': final_index - total_invested,
                    'return': index_return
                }
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Calculation error: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
