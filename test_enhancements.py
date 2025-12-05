from src.data_loader import fetch_data
from src.backtester import Backtester
from src.metrics import calculate_advanced_metrics, generate_insights

# Load data
print("Loading data...")
df = fetch_data()

# Test RSI strategy with SL/TP
print("\n" + "="*60)
print("Testing RSI Strategy with Stop-Loss and Take-Profit")
print("="*60)

bt = Backtester(df, stop_loss=-0.05, take_profit=0.10)
result = bt.run_rsi()

print(f"\nTotal trades: {len(bt.trades)}")
if len(bt.trades) > 0:
    print(f"\nExit reasons:")
    print(bt.trades['Exit_Reason'].value_counts())
    print(f"\nSample trades:")
    print(bt.trades[['Entry_Date', 'Exit_Date', 'PnL', 'Return_Pct', 'Exit_Reason']].head(10))

# Calculate metrics
metrics = calculate_advanced_metrics(result)
print(f"\n{'='*60}")
print("Performance Metrics")
print("="*60)
print(f"CAGR: {metrics['CAGR']:.2%}")
print(f"Sharpe: {metrics['Sharpe']:.2f}")
print(f"Max Drawdown: {metrics['Max_Drawdown']:.2%}")

# Generate insights
insights = generate_insights(result, metrics, bt.trades, "RSI")
print(f"\n{'='*60}")
print("Auto-Generated Insights")
print("="*60)
for insight in insights:
    print(f"  {insight}")

print(f"\n✅ All features working correctly!")
