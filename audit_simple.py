import json
import pandas as pd
import numpy as np

# Load metrics.json
with open('outputs/metrics.json', 'r') as f:
    metrics = json.load(f)

print("DECLARED METRICS (from metrics.json):")
print(f"CAGR: {metrics['cagr']*100:.2f}%")
print(f"Sharpe: {metrics['sharpe']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']*100:.2f}%")
print(f"Total Return: {metrics['total_return']*100:.1f}%")

# Load and verify from daily returns
df = pd.read_csv('outputs/strategy_results.csv', index_col=0, parse_dates=True)
returns = df['Strategy_Return']

# Compute equity
equity = (1 + returns).cumprod()
final_equity = equity.iloc[-1]

# Time period
years = (df.index[-1] - df.index[0]).days / 365.25

# CAGR
cagr = (final_equity ** (1/years)) - 1

# Sharpe
mean_daily = returns.mean()
std_daily = returns.std()
sharpe = (mean_daily * 252) / (std_daily * np.sqrt(252))

# Max DD
peak = equity.cummax()
dd = (equity - peak) / peak
max_dd = dd.min()

# Total return
total_ret = final_equity - 1

print("\nCOMPUTED METRICS (from daily returns):")
print(f"CAGR: {cagr*100:.2f}%")
print(f"Sharpe: {sharpe:.2f}")
print(f"Max Drawdown: {max_dd*100:.2f}%")
print(f"Total Return: {total_ret*100:.1f}%")

print("\nREADME CLAIMS:")
print("CAGR: 20.8%")
print("Sharpe: 1.31")
print("Max Drawdown: -8.8%")
print("Total Return: +690%")

print("\nMATCH STATUS:")
print(f"CAGR: {'YES' if abs(cagr - 0.208) < 0.005 else 'NO'}")
print(f"Sharpe: {'YES' if abs(sharpe - 1.31) < 0.05 else 'NO'}")
print(f"Max DD: {'YES' if abs(max_dd - (-0.088)) < 0.005 else 'NO'}")
print(f"Total Return: {'YES' if abs(total_ret - 6.9) < 0.1 else 'NO'}")
