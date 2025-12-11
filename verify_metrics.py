"""
Independent Metric Verification Script
Technical Auditor: Verifies performance claims against actual daily returns
"""

import pandas as pd
import numpy as np
from math import sqrt

def verify_metrics(csv_path):
    """
    Independently recompute metrics from daily returns CSV
    Uses strict mathematical definitions for reproducibility
    """
    
    # Load data
    df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    df = df.sort_values(df.index.name if df.index.name else 'Date').reset_index()
    
    # Extract returns
    r = df["Strategy_Return"].astype(float)
    
    # Equity curve (starting from 1.0)
    equity = (1 + r).cumprod()
    final = equity.iloc[-1]
    initial = 1.0
    
    # Time period
    date_col = df.columns[0]  # First column should be date
    start_date = pd.to_datetime(df[date_col].iloc[0])
    end_date = pd.to_datetime(df[date_col].iloc[-1])
    years = (end_date - start_date).days / 365.25
    
    # CAGR
    cagr = (final / initial)**(1/years) - 1
    
    # Sharpe Ratio (annualized)
    mean_daily = r.mean()
    std_daily = r.std(ddof=1)
    sharpe = (mean_daily * 252) / (std_daily * sqrt(252))
    
    # Max Drawdown
    peak = equity.cummax()
    drawdown = equity / peak - 1
    max_dd = drawdown.min()
    
    # Total Return
    total_return = final - 1
    
    return {
        "CAGR": cagr,
        "Sharpe": sharpe,
        "Max_Drawdown": max_dd,
        "Total_Return": total_return,
        "Start_Date": start_date,
        "End_Date": end_date,
        "Years": years,
        "Rows": len(df)
    }

def compare_metrics(computed, declared):
    """
    Compare computed vs declared metrics
    Returns match status and deviations
    """
    
    tolerance = {
        "CAGR": 0.001,  # 0.1% tolerance
        "Sharpe": 0.01,  # 0.01 tolerance
        "Max_Drawdown": 0.001,  # 0.1% tolerance
        "Total_Return": 0.01  # 1% tolerance
    }
    
    results = {}
    for key in ["CAGR", "Sharpe", "Max_Drawdown", "Total_Return"]:
        comp_val = computed[key]
        decl_val = declared[key]
        diff = abs(comp_val - decl_val)
        
        if key == "Sharpe":
            match = diff < tolerance[key]
        else:
            match = diff < tolerance[key]
        
        results[key] = {
            "computed": comp_val,
            "declared": decl_val,
            "diff": diff,
            "match": match
        }
    
    return results

if __name__ == "__main__":
    
    # Declared metrics from README
    declared = {
        "CAGR": 0.208,  # 20.8%
        "Sharpe": 1.31,
        "Max_Drawdown": -0.088,  # -8.8%
        "Total_Return": 6.90  # +690%
    }
    
    # Compute from actual data
    print("="*80)
    print("TECHNICAL AUDIT: NIFTY50 Backtester Performance Verification")
    print("="*80)
    print("\nLoading strategy_results.csv and recomputing metrics...")
    
    computed = verify_metrics("outputs/strategy_results.csv")
    
    print(f"\nData Summary:")
    print(f"  Rows: {computed['Rows']}")
    print(f"  Start Date: {computed['Start_Date'].strftime('%Y-%m-%d')}")
    print(f"  End Date: {computed['End_Date'].strftime('%Y-%m-%d')}")
    print(f"  Years: {computed['Years']:.2f}")
    
    # Compare
    comparison = compare_metrics(computed, declared)
    
    print("\n" + "="*80)
    print("VERIFICATION RESULTS")
    print("="*80)
    
    print("\n📊 Computed Metrics (from daily returns):")
    print(f"  • CAGR: {computed['CAGR']:.2%}")
    print(f"  • Sharpe: {computed['Sharpe']:.2f}")
    print(f"  • Max Drawdown: {computed['Max_Drawdown']:.2%}")
    print(f"  • Total Return: {computed['Total_Return']:.1%}")
    
    print("\n📋 Declared Metrics (from README):")
    print(f"  • CAGR: {declared['CAGR']:.1%}")
    print(f"  • Sharpe: {declared['Sharpe']:.2f}")
    print(f"  • Max Drawdown: {declared['Max_Drawdown']:.1%}")
    print(f"  • Total Return: {declared['Total_Return']:.0%}")
    
    print("\n✅ Match Status:")
    all_match = True
    for key in ["CAGR", "Sharpe", "Max_Drawdown", "Total_Return"]:
        status = "✓ YES" if comparison[key]["match"] else "✗ NO"
        diff_pct = comparison[key]["diff"]
        print(f"  • {key}: {status} (diff: {diff_pct:.4f})")
        if not comparison[key]["match"]:
            all_match = False
    
    print("\n" + "="*80)
    if all_match:
        print("🎯 VERDICT: The README claims are ACCURATE")
        print("All metrics match within acceptable tolerance.")
    else:
        print("⚠️  VERDICT: The README claims are PARTIALLY ACCURATE")
        print("Some metrics show deviations beyond tolerance.")
    print("="*80)
    
    # Detailed breakdown
    print("\n📝 Detailed Breakdown:")
    print(f"  CAGR: Declared {declared['CAGR']:.2%} | Computed {computed['CAGR']:.2%}")
    print(f"  Sharpe: Declared {declared['Sharpe']:.2f} | Computed {computed['Sharpe']:.2f}")
    print(f"  Max DD: Declared {declared['Max_Drawdown']:.2%} | Computed {computed['Max_Drawdown']:.2%}")
    print(f"  Total Return: Declared {declared['Total_Return']:.0%} | Computed {computed['Total_Return']:.0%}")
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE")
    print("="*80)
