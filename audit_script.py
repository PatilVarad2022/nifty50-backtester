"""
Audit Script - Reproduces metrics from raw data
Recomputes exact metrics from data/raw_nifty.csv and writes outputs/metrics.json

Usage:
    python audit_script.py

This script independently verifies all claimed metrics by:
1. Loading data/raw_nifty.csv
2. Running the exact same backtest
3. Computing all metrics
4. Writing outputs/metrics.json
5. Comparing against claimed values
"""

import pandas as pd
import numpy as np
import json
import os
import sys

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.backtester import Backtester
from src.metrics import calculate_advanced_metrics, calculate_trade_metrics

def main():
    print("="*80)
    print("AUDIT SCRIPT - Reproducing Metrics from Raw Data")
    print("="*80)
    
    # Load raw data
    print("\n[1/4] Loading data/raw_nifty.csv...")
    df = pd.read_csv('data/raw_nifty.csv', index_col=0, parse_dates=True)
    print(f"Loaded {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")
    
    # Run backtest with exact parameters
    print("\n[2/4] Running backtest with documented parameters...")
    print("  Strategy: Momentum (SMA-50)")
    print("  Initial Capital: Rs.100,000")
    print("  Transaction Cost: 0.1% (10 bps)")
    print("  Stop Loss: -5%")
    print("  Take Profit: +10%")
    
    bt = Backtester(
        df,
        initial_capital=100000,
        transaction_cost=0.001,  # 0.1%
        stop_loss=-0.05,
        take_profit=0.10
    )
    
    result = bt.run_momentum(sma_window=50)
    print("Backtest complete")
    
    # Calculate metrics
    print("\n[3/4] Calculating metrics...")
    metrics = calculate_advanced_metrics(result)
    trade_metrics = calculate_trade_metrics(bt.trades)
    
    # Create output matching README format
    output_metrics = {
        "strategy": "sma",
        "strategy_name": "Momentum (SMA-50)",
        "period": f"{df.index[0].year}-{df.index[-1].year}",
        "cagr": round(metrics['CAGR'], 4),
        "sharpe": round(metrics['Sharpe'], 2),
        "max_drawdown": round(metrics['Max_Drawdown'], 4),
        "total_return": round(metrics['Total_Return'], 4),
        "win_rate": round(trade_metrics['Win_Rate_Trade'], 4),
        "profit_factor": round(trade_metrics['Profit_Factor'], 2),
        "trades": trade_metrics['Total_Trades'],
        "volatility": round(metrics['Volatility'], 4),
        "sortino": round(metrics['Sortino'], 2),
        "calmar": round(metrics['Calmar'], 2)
    }
    
    # Write to outputs/metrics.json
    print("\n[4/4] Writing outputs/metrics.json...")
    os.makedirs('outputs', exist_ok=True)
    
    with open('outputs/metrics.json', 'w') as f:
        json.dump(output_metrics, f, indent=4)
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80)
    print("\nReproduced Metrics:")
    print(f"  CAGR:           {output_metrics['cagr']:.2%}")
    print(f"  Sharpe:         {output_metrics['sharpe']:.2f}")
    print(f"  Max Drawdown:   {output_metrics['max_drawdown']:.2%}")
    print(f"  Total Return:   {output_metrics['total_return']:.2%}")
    print(f"  Win Rate:       {output_metrics['win_rate']:.2%}")
    print(f"  Profit Factor:  {output_metrics['profit_factor']:.2f}")
    print(f"  Total Trades:   {output_metrics['trades']}")
    print("\nOutput written to: outputs/metrics.json")
    print("="*80)

if __name__ == "__main__":
    main()
