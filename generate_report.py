"""
Generate a comprehensive performance summary report.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import fetch_data
from backtester import Backtester
from metrics import calculate_advanced_metrics, calculate_drawdown_recovery, calculate_trade_metrics
from analysis import compare_with_benchmark, analyze_market_regimes
import pandas as pd
from datetime import datetime

def generate_report(strategy='momentum', sma_window=50, std_dev=2.0):
    """
    Generate a comprehensive text report for a strategy.
    """
    print("="*80)
    print("NIFTY 50 BACKTESTING REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Strategy: {strategy.upper()}")
    
    if strategy.lower() == 'momentum':
        print(f"Parameters: SMA Window = {sma_window}")
    else:
        print(f"Parameters: SMA Window = {sma_window}, Bollinger Bands = {std_dev}σ")
    
    print("\n" + "-"*80)
    print("DATA SUMMARY")
    print("-"*80)
    
    df = fetch_data()
    print(f"Period: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"Total Trading Days: {len(df)}")
    print(f"Market: NIFTY 50 (^NSEI)")
    
    # Run backtest
    bt = Backtester(df, transaction_cost=0.001)
    
    if strategy.lower() == 'momentum':
        res_df = bt.run_momentum(sma_window=sma_window)
    else:
        res_df = bt.run_mean_reversion(sma_window=sma_window, std_dev=std_dev)
    
    # Calculate metrics
    metrics = calculate_advanced_metrics(res_df)
    trade_metrics = calculate_trade_metrics(bt.trades)
    dd_recovery = calculate_drawdown_recovery(res_df)
    benchmark = compare_with_benchmark(res_df)
    
    print("\n" + "-"*80)
    print("PERFORMANCE METRICS")
    print("-"*80)
    print(f"Total Return:        {metrics['Total_Return']:>10.2%}")
    print(f"CAGR:                {metrics['CAGR']:>10.2%}")
    print(f"Volatility (Annual): {metrics['Volatility']:>10.2%}")
    print(f"Market Exposure:     {metrics['Market_Exposure']:>10.1%}")
    
    print("\n" + "-"*80)
    print("RISK-ADJUSTED RETURNS")
    print("-"*80)
    print(f"Sharpe Ratio:        {metrics['Sharpe']:>10.2f}")
    print(f"Sortino Ratio:       {metrics['Sortino']:>10.2f}")
    print(f"Calmar Ratio:        {metrics['Calmar']:>10.2f}")
    print(f"Stability (R²):      {metrics['Stability']:>10.2f}")
    
    print("\n" + "-"*80)
    print("DRAWDOWN ANALYSIS")
    print("-"*80)
    print(f"Max Drawdown:        {metrics['Max_Drawdown']:>10.2%}")
    print(f"Peak Date:           {dd_recovery['Peak_Date'].strftime('%Y-%m-%d'):>10}")
    print(f"Trough Date:         {dd_recovery['Trough_Date'].strftime('%Y-%m-%d'):>10}")
    
    if dd_recovery['Recovery_Date']:
        print(f"Recovery Date:       {dd_recovery['Recovery_Date'].strftime('%Y-%m-%d'):>10}")
        print(f"Recovery Duration:   {dd_recovery['Recovery_Days']:>10} days")
    else:
        print(f"Recovery Date:       {'Not Recovered':>10}")
    
    print("\n" + "-"*80)
    print("TRADE STATISTICS")
    print("-"*80)
    print(f"Total Trades:        {trade_metrics['Total_Trades']:>10}")
    print(f"Win Rate:            {trade_metrics['Win_Rate_Trade']:>10.1%}")
    print(f"Avg Trade Duration:  {trade_metrics['Avg_Trade_Duration']:>10.1f} days")
    print(f"Avg Win:             ₹{trade_metrics['Avg_Win']:>9.2f}")
    print(f"Avg Loss:            ₹{trade_metrics['Avg_Loss']:>9.2f}")
    print(f"Profit Factor:       {trade_metrics['Profit_Factor']:>10.2f}")
    
    print("\n" + "-"*80)
    print("RETURN DISTRIBUTION")
    print("-"*80)
    print(f"Skewness:            {metrics['Skewness']:>10.3f}")
    print(f"Kurtosis:            {metrics['Kurtosis']:>10.3f}")
    print(f"Daily Win Rate:      {metrics['Win_Rate_Daily']:>10.1%}")
    
    print("\n" + "-"*80)
    print("BENCHMARK COMPARISON (Buy & Hold)")
    print("-"*80)
    print(f"{'Metric':<20} {'Strategy':>15} {'Buy & Hold':>15} {'Difference':>15}")
    print("-"*80)
    print(f"{'CAGR':<20} {metrics['CAGR']:>14.2%} {benchmark['CAGR']:>14.2%} {metrics['CAGR']-benchmark['CAGR']:>14.2%}")
    print(f"{'Sharpe Ratio':<20} {metrics['Sharpe']:>14.2f} {benchmark['Sharpe']:>14.2f} {metrics['Sharpe']-benchmark['Sharpe']:>14.2f}")
    print(f"{'Max Drawdown':<20} {metrics['Max_Drawdown']:>14.2%} {benchmark['Max_Drawdown']:>14.2%} {metrics['Max_Drawdown']-benchmark['Max_Drawdown']:>14.2%}")
    print(f"{'Volatility':<20} {metrics['Volatility']:>14.2%} {benchmark['Volatility']:>14.2%} {metrics['Volatility']-benchmark['Volatility']:>14.2%}")
    
    # Market Regimes
    print("\n" + "-"*80)
    print("MARKET REGIME PERFORMANCE")
    print("-"*80)
    regime_df = analyze_market_regimes(res_df)
    print(regime_df.to_string(index=False))
    
    print("\n" + "="*80)
    print("EXECUTION MODEL")
    print("="*80)
    print("• Signals execute at NEXT DAY OPEN")
    print("• Look-ahead bias eliminated via signal shifting")
    print("• Transaction cost: 10 bps (0.1%) per trade")
    print("• No slippage beyond transaction cost")
    
    print("\n" + "="*80)
    print("DISCLAIMER")
    print("="*80)
    print("This is a backtest for educational purposes only.")
    print("Past performance does not guarantee future results.")
    print("="*80)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate strategy report')
    parser.add_argument('--strategy', type=str, default='momentum', choices=['momentum', 'mean_reversion'])
    parser.add_argument('--sma', type=int, default=50)
    parser.add_argument('--std', type=float, default=2.0)
    
    args = parser.parse_args()
    
    generate_report(
        strategy=args.strategy,
        sma_window=args.sma,
        std_dev=args.std
    )
