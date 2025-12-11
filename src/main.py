import argparse
import json
import os
import sys
import pandas as pd

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_loader import fetch_data
from src.backtester import Backtester
from src.metrics import calculate_advanced_metrics, calculate_trade_metrics

def main():
    parser = argparse.ArgumentParser(description='Run NIFTY 50 Backtest')
    parser.add_argument('--strategy', type=str, required=True, choices=['sma', 'rsi', 'mean_reversion'], help='Strategy to run')
    parser.add_argument('--config', type=str, required=True, help='Path to config JSON file')
    args = parser.parse_args()

    # Load config
    try:
        with open(args.config, 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found at {args.config}")
        return

    # Fetch data
    try:
        # Use default kwargs or add support for date range in config if needed
        df = fetch_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    # Initialize Backtester
    # Extract backtester init args from config
    bt_args = {k: v for k, v in config.items() if k in ['initial_capital', 'transaction_cost', 'dividend_yield', 'stop_loss', 'take_profit', 'position_size']}
    bt = Backtester(df, **bt_args)

    # Run Strategy
    if args.strategy == 'sma':
        result = bt.run_momentum(sma_window=config.get('sma_window', 50))
    elif args.strategy == 'mean_reversion':
        result = bt.run_mean_reversion(sma_window=config.get('sma_window', 20), std_dev=config.get('std_dev', 2.0))
    elif args.strategy == 'rsi':
        result = bt.run_rsi(rsi_period=config.get('rsi_period', 14), oversold=config.get('oversold', 30), overbought=config.get('overbought', 70))

    # Calculate Metrics
    metrics = calculate_advanced_metrics(result)
    trade_metrics = calculate_trade_metrics(bt.trades)
    
    # Merge for easier access
    all_metrics = {**metrics, **trade_metrics}

    # Print Metrics (Snippet for README)
    print("\n" + "="*60)
    print(f"NIFTY50 Backtesting Engine — Evaluated {df.index[0].year}–{df.index[-1].year} {args.strategy.upper()} strategy:")
    print(f"• CAGR: {all_metrics['CAGR']:.1%}")
    print(f"• Sharpe: {all_metrics['Sharpe']:.2f}")
    print(f"• Max Drawdown: {all_metrics['Max_Drawdown']:.1%}")
    print(f"• Win Rate: {all_metrics['Win_Rate_Trade']:.0%}")
    print(f"• Total Returns: {all_metrics['Total_Return']:.0%}")
    print("="*60 + "\n")

    # Ensure data directory exists
    os.makedirs('data', exist_ok=True)

    # Save results
    result.to_csv('data/strategy_results.csv')
    bt.save_trade_log('data/trades.csv')
    
    # Save summary (Moderate fix)
    summary_df = pd.DataFrame([all_metrics])
    summary_df.to_csv('data/summary_metrics.csv', index=False)
    
    # Generate Plots for README
    try:
        import matplotlib.pyplot as plt
        
        # Equity Curve
        plt.figure(figsize=(10, 6))
        plt.plot(result.index, result['Strategy_Equity'], label='Strategy')
        plt.plot(result.index, result['Market_Equity'], label='Buy & Hold', alpha=0.7)
        plt.title(f'Equity Curve: {args.strategy.upper()} vs NIFTY 50')
        plt.xlabel('Date')
        plt.ylabel('Equity (INR)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.savefig('data/equity_curve.png')
        plt.close()
        
        # Drawdown
        cum_ret = (1 + result['Strategy_Return']).cumprod()
        peak = cum_ret.cummax()
        drawdown = (cum_ret - peak) / peak
        
        plt.figure(figsize=(10, 4))
        plt.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        plt.plot(drawdown.index, drawdown, color='red', linewidth=1)
        plt.title(f'Drawdown Profile: {args.strategy.upper()}')
        plt.xlabel('Date')
        plt.ylabel('Drawdown %')
        plt.grid(True, alpha=0.3)
        plt.savefig('data/drawdown.png')
        plt.close()
        print("Generated plots in data/equity_curve.png and data/drawdown.png")
        
    except ImportError:
        print("Matplotlib not installed, skipping plot generation")
    except Exception as e:
        print(f"Error generating plots: {e}")

    print("Results saved to data/strategy_results.csv, data/trades.csv and data/summary_metrics.csv")

if __name__ == "__main__":
    main()
