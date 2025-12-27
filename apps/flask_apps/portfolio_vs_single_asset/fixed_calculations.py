"""
Fixed calculation functions for portfolio simulation.
These functions correctly include the initial portfolio value and track total investment.
"""
import pandas as pd
import numpy as np
from typing import Dict


def simulate_portfolio(stock_prices: pd.DataFrame, contribution: float, initial_investment: float) -> pd.DataFrame:
    """
    Simulates portfolio growth over time for a multi-stock portfolio.
    
    FIXED: Now includes initial portfolio value and tracks total investment.
    """
    periods = stock_prices.index
    num_tickers = len(stock_prices.columns)
    
    # The contribution per period is split equally among stocks
    period_contribution = contribution / num_tickers
    
    # Initialize tracking variables
    shares_bought: Dict[str, np.ndarray] = {ticker: np.zeros(len(stock_prices)) for ticker in stock_prices.columns}
    leftover_cash: Dict[str, float] = {ticker: 0.0 for ticker in stock_prices.columns}
    initial_per_stock = initial_investment / num_tickers
    
    # Track total invested amount
    total_invested = initial_investment
    total_invested_list = [total_invested]

    # At the first period, buy as many whole shares as possible with initial investment
    portfolio_value_initial = 0.0
    for ticker in stock_prices.columns:
        price = stock_prices[ticker].iloc[0]
        initial_shares = initial_per_stock // price
        leftover_cash[ticker] = initial_per_stock % price
        shares_bought[ticker][0] = initial_shares
        portfolio_value_initial += shares_bought[ticker][0] * price

    portfolio_values = [portfolio_value_initial]
    
    # For subsequent periods, add contributions and buy more shares
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
    """
    Simulates index investment growth over time.
    
    FIXED: Now includes initial portfolio value and tracks total investment.
    """
    periods = index_prices.index
    shares_bought = np.zeros(len(index_prices))
    leftover_cash = 0.0
    
    # Track total invested amount
    total_invested = initial_investment
    total_invested_list = [total_invested]

    # Initial purchase with initial investment
    price_initial = index_prices.iloc[0]
    initial_shares = initial_investment // price_initial
    leftover_cash = initial_investment % price_initial
    shares_bought[0] = initial_shares
    
    # Calculate initial portfolio value
    portfolio_values = [shares_bought[0] * price_initial]
    
    # For subsequent periods, add contributions and buy more shares
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
