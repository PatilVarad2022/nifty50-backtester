import argparse
import json
import os
import sys
import pandas as pd

# Add src to path just in case
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_loader import fetch_data
from src.backtester import Backtester
from src.metrics import (calculate_advanced_metrics, calculate_trade_metrics, 
                         calculate_additional_risk_metrics, compare_strategy_benchmark,
                         generate_insights)
from src.plots import generate_all_plots

def main():
    parser = argparse.ArgumentParser(description='Run NIFTY 50 Backtest with Comprehensive Analysis')
    parser.add_argument('--data', type=str, required=False, help='Path to data CSV')
    parser.add_argument('--out', type=str, default='outputs/', help='Output directory')
    parser.add_argument('--strategy', type=str, default='sma', choices=['sma', 'rsi', 'mean_reversion'], help='Strategy to run')
    parser.add_argument('--config', type=str, default='configs/sma.json', help='Path to config JSON file')
    parser.add_argument('--generate-plots', action='store_true', default=True, help='Generate comprehensive plots')
    parser.add_argument('--benchmark', action='store_true', default=True, help='Include benchmark comparison')
    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.out, exist_ok=True)

    # Load config (fallback to defaults if file missing)
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

    print(f"\n{'='*70}")
    print(f"NIFTY 50 Professional Backtesting Engine")
    print(f"{'='*70}")
    print(f"Data Period: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
    print(f"Total Days: {len(df)}")
    print(f"Strategy: {args.strategy.upper()}")
    print(f"{'='*70}\n")

    # Initialize Backtester
    bt = Backtester(df, 
                    initial_capital=config.get('initial_capital', 100000),
                    transaction_cost=config.get('transaction_cost', 0.001),
                    stop_loss=config.get('stop_loss', -0.05), 
                    take_profit=config.get('take_profit', 0.10)
                    )

    # Run Strategy
    print(f"Running {args.strategy.upper()} strategy...")
    if args.strategy == 'sma':
        result = bt.run_momentum(sma_window=config.get('sma_window', 50))
        strategy_name = f"Momentum (SMA-{config.get('sma_window', 50)})"
    elif args.strategy == 'mean_reversion':
        result = bt.run_mean_reversion(sma_window=config.get('sma_window', 20), std_dev=config.get('std_dev', 2.0))
        strategy_name = f"Mean Reversion (BB-{config.get('sma_window', 20)})"
    elif args.strategy == 'rsi':
        result = bt.run_rsi(rsi_period=config.get('rsi_period', 14), oversold=config.get('oversold', 30), overbought=config.get('overbought', 70))
        strategy_name = f"RSI ({config.get('rsi_period', 14)})"

    print("✓ Strategy execution complete\n")

    # Calculate Comprehensive Metrics
    print("Calculating performance metrics...")
    metrics = calculate_advanced_metrics(result)
    trade_metrics = calculate_trade_metrics(bt.trades)
    risk_metrics = calculate_additional_risk_metrics(result)
    
    # Merge all metrics
    all_metrics = {**metrics, **trade_metrics, **risk_metrics}
    
    print("✓ Metrics calculation complete\n")

    # Benchmark Comparison
    if args.benchmark:
        print("Calculating benchmark (Buy & Hold) metrics...")
        # Create a simple buy-and-hold result from the Market_Equity column
        benchmark_df = result.copy()
        benchmark_df['Strategy_Return'] = benchmark_df['Market_Return']
        benchmark_df['Strategy_Equity'] = benchmark_df['Market_Equity']
        benchmark_df['Position'] = 1.0  # Always invested
        
        benchmark_metrics = calculate_advanced_metrics(benchmark_df)
        comparison_df = compare_strategy_benchmark(metrics, benchmark_metrics)
        
        # Save comparison
        comparison_path = os.path.join(args.out, 'benchmark_comparison.csv')
        comparison_df.to_csv(comparison_path, index=False)
        print(f"✓ Benchmark comparison saved to {comparison_path}\n")

    # Generate Insights
    print("Generating performance insights...")
    insights = generate_insights(result, metrics, bt.trades, strategy_name)
    
    # Print Summary Report
    print(f"\n{'='*70}")
    print(f"PERFORMANCE SUMMARY: {strategy_name}")
    print(f"{'='*70}\n")
    
    print("📊 RETURNS & RISK-ADJUSTED PERFORMANCE")
    print(f"  • CAGR:                    {metrics['CAGR']:>8.2%}")
    print(f"  • Total Return:            {metrics['Total_Return']:>8.2%}")
    print(f"  • Sharpe Ratio:            {metrics['Sharpe']:>8.2f}")
    print(f"  • Sortino Ratio:           {metrics['Sortino']:>8.2f}")
    print(f"  • Calmar Ratio:            {metrics['Calmar']:>8.2f}")
    
    print(f"\n🛡️  RISK METRICS")
    print(f"  • Max Drawdown:            {metrics['Max_Drawdown']:>8.2%}")
    print(f"  • Volatility (Annual):     {metrics['Volatility']:>8.2%}")
    print(f"  • VaR (95%):               {risk_metrics['VaR_95']:>8.2%}")
    print(f"  • CVaR (95%):              {risk_metrics['CVaR_95']:>8.2%}")
    print(f"  • Ulcer Index:             {risk_metrics['Ulcer_Index']:>8.2f}")
    
    print(f"\n📈 TRADE STATISTICS")
    print(f"  • Total Trades:            {trade_metrics['Total_Trades']:>8.0f}")
    print(f"  • Win Rate (Trade):        {trade_metrics['Win_Rate_Trade']:>8.2%}")
    print(f"  • Hit Rate (Daily):        {risk_metrics['Hit_Rate']:>8.2%}")
    print(f"  • Profit Factor:           {trade_metrics['Profit_Factor']:>8.2f}")
    print(f"  • Avg Trade Duration:      {trade_metrics['Avg_Trade_Duration']:>8.1f} days")
    
    print(f"\n💡 KEY INSIGHTS")
    for insight in insights:
        print(f"  {insight}")
    
    if args.benchmark:
        print(f"\n🎯 VS BENCHMARK (Buy & Hold)")
        print(f"  • CAGR Difference:         {metrics['CAGR'] - benchmark_metrics['CAGR']:>+8.2%}")
        print(f"  • Sharpe Difference:       {metrics['Sharpe'] - benchmark_metrics['Sharpe']:>+8.2f}")
        print(f"  • Max DD Difference:       {metrics['Max_Drawdown'] - benchmark_metrics['Max_Drawdown']:>+8.2%}")
    
    print(f"\n{'='*70}\n")

    # Save results
    print("Saving results...")
    result_path = os.path.join(args.out, 'strategy_results.csv')
    trades_path = os.path.join(args.out, 'trades.csv')
    metrics_path = os.path.join(args.out, 'metrics.json')
    full_metrics_path = os.path.join(args.out, 'full_metrics.json')
    
    result.to_csv(result_path)
    bt.save_trade_log(trades_path)
    
    # Save recruiter-friendly metrics JSON
    recruiter_metrics = {
        "strategy": args.strategy,
        "strategy_name": strategy_name,
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
    
    with open(metrics_path, 'w') as f:
        json.dump(recruiter_metrics, f, indent=4)
    
    # Save full metrics (for analysis)
    with open(full_metrics_path, 'w') as f:
        # Convert numpy types to Python types for JSON serialization
        json_metrics = {k: float(v) if isinstance(v, (int, float)) else v 
                       for k, v in all_metrics.items()}
        json.dump(json_metrics, f, indent=4)
    
    print(f"✓ Results saved to {result_path}")
    print(f"✓ Trades saved to {trades_path}")
    print(f"✓ Metrics saved to {metrics_path}")

    # Generate Comprehensive Plots
    if args.generate_plots:
        print(f"\nGenerating comprehensive visualizations...")
        try:
            generate_all_plots(result, bt.trades, strategy_name, args.out)
            print("✓ All plots generated successfully")
        except Exception as e:
            print(f"⚠ Error generating plots: {e}")
            import traceback
            traceback.print_exc()

    print(f"\n{'='*70}")
    print(f"✅ BACKTEST COMPLETE")
    print(f"{'='*70}")
    print(f"All outputs saved to: {os.path.abspath(args.out)}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()
