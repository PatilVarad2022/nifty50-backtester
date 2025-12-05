"""
Multi-Strategy Comparison Script
Generates comprehensive comparison across all strategy configurations.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_loader import fetch_data
from analysis import multi_strategy_comparison, split_data
from backtester import Backtester
from metrics import calculate_advanced_metrics, calculate_trade_metrics
import pandas as pd

def main():
    print("Loading NIFTY 50 data...")
    df = fetch_data()
    
    print("\n" + "="*80)
    print("FULL PERIOD ANALYSIS (2015-2023)")
    print("="*80)
    
    comparison_df = multi_strategy_comparison(df)
    print(comparison_df.to_string(index=False))
    
    # Save to CSV
    comparison_df.to_csv("data/multi_strategy_comparison.csv", index=False)
    print("\n✅ Saved to data/multi_strategy_comparison.csv")
    
    # In-sample vs Out-of-sample
    print("\n" + "="*80)
    print("IN-SAMPLE vs OUT-OF-SAMPLE ANALYSIS")
    print("="*80)
    
    train_df, test_df = split_data(df, train_end='2023-12-31')
    
    print(f"\nTrain Period: {train_df.index[0]} to {train_df.index[-1]}")
    print(f"Test Period: {test_df.index[0]} to {test_df.index[-1]}")
    
    
    # Test best strategies on both periods
    configs = [
        ("Momentum SMA=50", "run_momentum", {"sma_window": 50}),
        ("Mean Reversion", "run_mean_reversion", {"sma_window": 20, "std_dev": 2.0}),
        ("RSI", "run_rsi", {"rsi_period": 14, "oversold": 30, "overbought": 70})
    ]
    
    results = []
    
    for name, method, params in configs:
        # Train
        bt_train = Backtester(train_df)
        res_train = getattr(bt_train, method)(**params)
        metrics_train = calculate_advanced_metrics(res_train)
        
        # Test
        bt_test = Backtester(test_df)
        res_test = getattr(bt_test, method)(**params)
        metrics_test = calculate_advanced_metrics(res_test)
        
        results.append({
            "Strategy": name,
            "Train_CAGR": metrics_train['CAGR'],
            "Train_Sharpe": metrics_train['Sharpe'],
            "Train_MaxDD": metrics_train['Max_Drawdown'],
            "Test_CAGR": metrics_test['CAGR'],
            "Test_Sharpe": metrics_test['Sharpe'],
            "Test_MaxDD": metrics_test['Max_Drawdown']
        })
    
    split_df = pd.DataFrame(results)
    print("\n" + split_df.to_string(index=False))
    
    split_df.to_csv("data/in_sample_out_sample.csv", index=False)
    print("\n✅ Saved to data/in_sample_out_sample.csv")

if __name__ == "__main__":
    main()
