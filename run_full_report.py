"""
Full Reproducibility Runner
Runs the complete backtest pipeline and generates all outputs.

Usage:
    python run_full_report.py
"""

import subprocess
import sys
import os

def main():
    print("="*80)
    print("NIFTY 50 Backtester - Full Reproducibility Runner")
    print("="*80)
    
    # Step 1: Check if requirements are installed
    print("\n[1/3] Checking dependencies...")
    try:
        import pandas
        import numpy
        import yfinance
        import matplotlib
        import scipy
        import seaborn
        print("[OK] All dependencies installed")
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("\nPlease install requirements:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    # Step 2: Run backtest
    print("\n[2/3] Running backtest...")
    print("Command: python generate_report.py --data data/raw_nifty.csv --out outputs/ --strategy sma")
    
    result = subprocess.run([
        sys.executable,
        "generate_report.py",
        "--data", "data/raw_nifty.csv",
        "--out", "outputs/",
        "--strategy", "sma"
    ], capture_output=False)
    
    if result.returncode != 0:
        print("[ERROR] Backtest failed")
        sys.exit(1)
    
    print("\n[OK] Backtest complete")
    
    # Step 3: Run audit
    print("\n[3/3] Running independent audit...")
    result = subprocess.run([
        sys.executable,
        "audit_metrics.py"
    ], capture_output=False)
    
    if result.returncode != 0:
        print("[ERROR] Audit failed")
        sys.exit(1)
    
    print("\n[OK] Audit complete")
    
    # Summary
    print("\n" + "="*80)
    print("SUCCESS: Full reproducibility run complete")
    print("="*80)
    print("\nGenerated outputs:")
    print("  - outputs/metrics.json")
    print("  - outputs/full_metrics.json")
    print("  - outputs/strategy_results.csv")
    print("  - outputs/trades.csv")
    print("  - outputs/benchmark_comparison.csv")
    print("  - outputs/cost_sensitivity.csv")
    print("  - outputs/*.png (6 visualizations)")
    print("\nAll metrics independently verified via audit_metrics.py")
    print("="*80)

if __name__ == "__main__":
    main()
