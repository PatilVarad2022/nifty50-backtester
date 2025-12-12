"""
Independent Audit & Verification Script
Reproduces and verifies all claimed metrics from the README.

This script:
1. Loads the same data used in the backtest
2. Runs the SMA-50 strategy with documented parameters
3. Recalculates all metrics independently
4. Compares against claimed values
5. Reports any discrepancies

Run this to verify the accuracy of reported performance metrics.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime

# Import backtesting modules
from src.backtester import Backtester
from src.metrics import calculate_advanced_metrics, calculate_trade_metrics, calculate_additional_risk_metrics

def audit_metrics():
    """
    Independent verification of reported metrics.
    """
    print("="*80)
    print("INDEPENDENT AUDIT & VERIFICATION")
    print("="*80)
    print(f"Audit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Auditor: Automated Verification Script")
    print("="*80)
    
    # Load claimed metrics
    print("\n[1/5] Loading claimed metrics from outputs/metrics.json...")
    with open('outputs/metrics.json', 'r') as f:
        claimed_metrics = json.load(f)
    
    print(f"✓ Claimed Strategy: {claimed_metrics['strategy']}")
    print(f"✓ Claimed Period: {claimed_metrics['period']}")
    print(f"✓ Claimed CAGR: {claimed_metrics['cagr']:.2%}")
    print(f"✓ Claimed Sharpe: {claimed_metrics['sharpe']:.2f}")
    
    # Load data
    print("\n[2/5] Loading market data...")
    df = pd.read_csv('data/raw_nifty.csv', index_col=0, parse_dates=True)
    print(f"✓ Data loaded: {len(df)} rows from {df.index[0].date()} to {df.index[-1].date()}")
    
    # Run backtest with documented parameters
    print("\n[3/5] Running backtest with documented parameters...")
    print("  Parameters:")
    print("    - Strategy: Momentum (SMA-50)")
    print("    - Initial Capital: ₹100,000")
    print("    - Transaction Cost: 0.1% (10 bps)")
    print("    - Stop Loss: -5%")
    print("    - Take Profit: +10%")
    
    bt = Backtester(
        df, 
        initial_capital=100000,
        transaction_cost=0.001,  # 0.1%
        stop_loss=-0.05,
        take_profit=0.10
    )
    
    result = bt.run_momentum(sma_window=50)
    print("✓ Backtest complete")
    
    # Calculate metrics
    print("\n[4/5] Calculating metrics independently...")
    metrics = calculate_advanced_metrics(result)
    trade_metrics = calculate_trade_metrics(bt.trades)
    risk_metrics = calculate_additional_risk_metrics(result)
    
    print("✓ Metrics calculated")
    
    # Verify metrics
    print("\n[5/5] Verifying metrics...")
    print("\n" + "="*80)
    print("VERIFICATION RESULTS")
    print("="*80)
    
    discrepancies = []
    tolerance = 0.01  # 1% tolerance for rounding
    
    # Check CAGR
    cagr_diff = abs(metrics['CAGR'] - claimed_metrics['cagr'])
    cagr_match = cagr_diff < tolerance
    print(f"\nCAGR:")
    print(f"  Claimed:    {claimed_metrics['cagr']:.4f} ({claimed_metrics['cagr']:.2%})")
    print(f"  Calculated: {metrics['CAGR']:.4f} ({metrics['CAGR']:.2%})")
    print(f"  Difference: {cagr_diff:.4f}")
    print(f"  Status:     {'✓ VERIFIED' if cagr_match else '✗ DISCREPANCY'}")
    if not cagr_match:
        discrepancies.append(f"CAGR: {cagr_diff:.4f} difference")
    
    # Check Sharpe
    sharpe_diff = abs(metrics['Sharpe'] - claimed_metrics['sharpe'])
    sharpe_match = sharpe_diff < 0.05  # 0.05 tolerance for Sharpe
    print(f"\nSharpe Ratio:")
    print(f"  Claimed:    {claimed_metrics['sharpe']:.2f}")
    print(f"  Calculated: {metrics['Sharpe']:.2f}")
    print(f"  Difference: {sharpe_diff:.2f}")
    print(f"  Status:     {'✓ VERIFIED' if sharpe_match else '✗ DISCREPANCY'}")
    if not sharpe_match:
        discrepancies.append(f"Sharpe: {sharpe_diff:.2f} difference")
    
    # Check Max Drawdown
    dd_diff = abs(metrics['Max_Drawdown'] - claimed_metrics['max_drawdown'])
    dd_match = dd_diff < tolerance
    print(f"\nMax Drawdown:")
    print(f"  Claimed:    {claimed_metrics['max_drawdown']:.4f} ({claimed_metrics['max_drawdown']:.2%})")
    print(f"  Calculated: {metrics['Max_Drawdown']:.4f} ({metrics['Max_Drawdown']:.2%})")
    print(f"  Difference: {dd_diff:.4f}")
    print(f"  Status:     {'✓ VERIFIED' if dd_match else '✗ DISCREPANCY'}")
    if not dd_match:
        discrepancies.append(f"Max DD: {dd_diff:.4f} difference")
    
    # Check Total Return
    tr_diff = abs(metrics['Total_Return'] - claimed_metrics['total_return'])
    tr_match = tr_diff < tolerance
    print(f"\nTotal Return:")
    print(f"  Claimed:    {claimed_metrics['total_return']:.4f} ({claimed_metrics['total_return']:.2%})")
    print(f"  Calculated: {metrics['Total_Return']:.4f} ({metrics['Total_Return']:.2%})")
    print(f"  Difference: {tr_diff:.4f}")
    print(f"  Status:     {'✓ VERIFIED' if tr_match else '✗ DISCREPANCY'}")
    if not tr_match:
        discrepancies.append(f"Total Return: {tr_diff:.4f} difference")
    
    # Check Win Rate
    wr_diff = abs(trade_metrics['Win_Rate_Trade'] - claimed_metrics['win_rate'])
    wr_match = wr_diff < tolerance
    print(f"\nWin Rate:")
    print(f"  Claimed:    {claimed_metrics['win_rate']:.4f} ({claimed_metrics['win_rate']:.2%})")
    print(f"  Calculated: {trade_metrics['Win_Rate_Trade']:.4f} ({trade_metrics['Win_Rate_Trade']:.2%})")
    print(f"  Difference: {wr_diff:.4f}")
    print(f"  Status:     {'✓ VERIFIED' if wr_match else '✗ DISCREPANCY'}")
    if not wr_match:
        discrepancies.append(f"Win Rate: {wr_diff:.4f} difference")
    
    # Check Trade Count
    trades_match = trade_metrics['Total_Trades'] == claimed_metrics['trades']
    print(f"\nTotal Trades:")
    print(f"  Claimed:    {claimed_metrics['trades']}")
    print(f"  Calculated: {trade_metrics['Total_Trades']}")
    print(f"  Status:     {'✓ VERIFIED' if trades_match else '✗ DISCREPANCY'}")
    if not trades_match:
        discrepancies.append(f"Trades: {abs(trade_metrics['Total_Trades'] - claimed_metrics['trades'])} difference")
    
    # Final verdict
    print("\n" + "="*80)
    if len(discrepancies) == 0:
        print("✓ AUDIT PASSED: All metrics verified within tolerance")
        print("="*80)
        return True
    else:
        print("✗ AUDIT FAILED: Discrepancies found:")
        for disc in discrepancies:
            print(f"  - {disc}")
        print("="*80)
        return False

if __name__ == "__main__":
    try:
        audit_passed = audit_metrics()
        exit(0 if audit_passed else 1)
    except Exception as e:
        print(f"\n✗ AUDIT ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
