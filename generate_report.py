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
    parser.add_argument('--data', type=str, required=False, help='Path to data CSV')
    parser.add_argument('--out', type=str, default='outputs/', help='Output directory')
    parser.add_argument('--strategy', type=str, default='sma', choices=['sma', 'rsi', 'mean_reversion'], help='Strategy to run')
    parser.add_argument('--config', type=str, default='configs/sma.json', help='Path to config JSON file')
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.out, exist_ok=True)

    # Load config (fallback to defaults if file missing)
    # This allows running with just command flags if config isn't needed for critical params
    config = {}
    if os.path.exists(args.config):
        with open(args.config, 'r') as f:
            config = json.load(f)

    # Fetch data
    try:
        if args.data:
             print(f"Loading data from {args.data}...")
             df = pd.read_csv(args.data, index_col=0, parse_dates=True)
             # Basic validation
             if df.empty:
                 raise ValueError("Data file is empty")
        else:
             df = fetch_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # Initialize Backtester
    # Prioritize loading from config if available, else defaults
    bt = Backtester(df, 
                    initial_capital=config.get('initial_capital', 100000),
                    transaction_cost=config.get('transaction_cost', 0.001),
                    stop_loss=config.get('stop_loss', -0.05), 
                    take_profit=config.get('take_profit', 0.10)
                    )

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
    
    # Merge and standardize keys for recruiter-friendly JSON (snake_case)
    recruiter_metrics = {
        "strategy": args.strategy,
        "cagr": metrics['CAGR'],
        "sharpe": metrics['Sharpe'],
        "max_drawdown": metrics['Max_Drawdown'],
        "total_return": metrics['Total_Return'],
        "win_rate": trade_metrics['Win_Rate_Trade'],
        "profit_factor": trade_metrics['Profit_Factor'],
        "trades": trade_metrics['Total_Trades']
    }

    # Print Metrics (Snippet for README)
    print("\n" + "="*60)
    print(f"NIFTY50 Backtesting Engine — Evaluated {df.index[0].year}–{df.index[-1].year} {args.strategy.upper()} strategy:")
    print(f"• CAGR: {recruiter_metrics['cagr']:.1%}")
    print(f"• Sharpe: {recruiter_metrics['sharpe']:.2f}")
    print(f"• Max Drawdown: {recruiter_metrics['max_drawdown']:.1%}")
    print(f"• Win Rate: {recruiter_metrics['win_rate']:.0%}")
    print(f"• Total Returns: {recruiter_metrics['total_return']:.0%}")
    print("="*60 + "\n")

    # Save results
    result_path = os.path.join(args.out, 'strategy_results.csv')
    trades_path = os.path.join(args.out, 'trades.csv')
    metrics_path = os.path.join(args.out, 'metrics.json')
    equity_path = os.path.join(args.out, 'equity_curve.png')
    
    result.to_csv(result_path)
    bt.save_trade_log(trades_path)
    
    # Save recruiter metrics JSON
    with open(metrics_path, 'w') as f:
        json.dump(recruiter_metrics, f, indent=4)
    
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
        plt.savefig(equity_path)
        plt.close()
        
        print(f"Generated plot: {equity_path}")
        
    except ImportError:
        print("Matplotlib not installed, skipping plot generation")
    except Exception as e:
        print(f"Error generating plots: {e}")

    print(f"Results saved to {args.out} directory")

if __name__ == "__main__":
    main()
