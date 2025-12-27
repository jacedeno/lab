import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_index_investment_buggy(index_prices: pd.Series, contribution: float, initial_investment: float) -> pd.DataFrame:
    """Original buggy version - missing initial value"""
    periods = index_prices.index
    shares_bought = np.zeros(len(index_prices))
    leftover_cash = 0.0

    initial_shares = initial_investment // index_prices.iloc[0]
    leftover_cash = initial_investment % index_prices.iloc[0]
    shares_bought[0] = initial_shares
    portfolio_values = []
    for i in range(1, len(periods)):
        price = index_prices.iloc[i]
        total_money = contribution + leftover_cash
        shares_to_buy = total_money // price
        leftover_cash = total_money % price
        shares_bought[i] = shares_bought[i - 1] + shares_to_buy
        portfolio_values.append(shares_bought[i] * price)  # BUG: Missing initial value!
    return pd.DataFrame({'Index Value': portfolio_values}, index=periods[1:])

def simulate_index_investment_fixed(index_prices: pd.Series, contribution: float, initial_investment: float) -> pd.DataFrame:
    """Fixed version - includes initial value"""
    periods = index_prices.index
    shares_bought = np.zeros(len(index_prices))
    leftover_cash = 0.0
    total_invested = 0.0

    # Initial purchase
    initial_shares = initial_investment // index_prices.iloc[0]
    leftover_cash = initial_investment % index_prices.iloc[0]
    shares_bought[0] = initial_shares
    total_invested = initial_investment
    
    # Calculate initial portfolio value
    portfolio_values = [shares_bought[0] * index_prices.iloc[0]]
    total_invested_list = [total_invested]
    
    # Subsequent periods
    for i in range(1, len(periods)):
        price = index_prices.iloc[i]
        total_money = contribution + leftover_cash
        shares_to_buy = total_money // price
        leftover_cash = total_money % price
        shares_bought[i] = shares_bought[i - 1] + shares_to_buy
        total_invested += contribution
        portfolio_values.append(shares_bought[i] * price)
        total_invested_list.append(total_invested)
    
    return pd.DataFrame({
        'Index Value': portfolio_values,
        'Total Invested': total_invested_list,
        'Shares Held': shares_bought
    }, index=periods)

# Test with user's scenario: $1,000 initial, $200 weekly for 6 years
print("Testing SPY investment simulation...")
print("Scenario: $1,000 initial + $200/week for ~6 years")
print("-" * 80)

# Download SPY data
start_date = datetime.now() - timedelta(days=6*365)
end_date = datetime.now()
spy_data = yf.download('SPY', start=start_date, end=end_date, interval='1wk', auto_adjust=True, progress=False)
spy_prices = spy_data['Close']

# Test buggy version
buggy_result = simulate_index_investment_buggy(spy_prices, 200, 1000)
print("\n=== BUGGY VERSION ===")
print(f"Number of data points: {len(buggy_result)}")
print(f"Final value: ${buggy_result['Index Value'].iloc[-1]:,.2f}")

# Test fixed version
fixed_result = simulate_index_investment_fixed(spy_prices, 200, 1000)
print("\n=== FIXED VERSION ===")
print(f"Number of data points: {len(fixed_result)}")
print(f"Number of weeks: {len(fixed_result)}")
print(f"Total invested: ${fixed_result['Total Invested'].iloc[-1]:,.2f}")
print(f"Final value: ${fixed_result['Index Value'].iloc[-1]:,.2f}")
print(f"Total shares: {fixed_result['Shares Held'].iloc[-1]:.2f}")
print(f"Return: ${(fixed_result['Index Value'].iloc[-1] - fixed_result['Total Invested'].iloc[-1]):,.2f}")
print(f"Return %: {((fixed_result['Index Value'].iloc[-1] / fixed_result['Total Invested'].iloc[-1]) - 1) * 100:.2f}%")

print("\n" + "=" * 80)
print("DIAGNOSIS:")
print("The buggy version is missing the initial portfolio value in the results,")
print("which causes the length mismatch and incorrect calculations.")
