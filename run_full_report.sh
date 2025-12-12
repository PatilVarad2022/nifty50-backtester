#!/bin/bash
# Full Reproducibility Runner
# One-command script to reproduce all results

set -e  # Exit on error

echo "================================================================================"
echo "NIFTY 50 Backtester - Full Reproducibility Runner"
echo "================================================================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "ERROR: Python not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies
echo ""
echo "[1/4] Installing dependencies..."
pip install -q -r requirements.txt
echo "Dependencies installed"

# Run backtest
echo ""
echo "[2/4] Running backtest..."
python generate_report.py --data data/raw_nifty.csv --out outputs/ --strategy sma
echo "Backtest complete"

# Generate SHA256 checksum
echo ""
echo "[3/4] Generating checksum..."
if command -v sha256sum &> /dev/null; then
    sha256sum outputs/metrics.json > outputs/metrics.sha256
elif command -v shasum &> /dev/null; then
    shasum -a 256 outputs/metrics.json > outputs/metrics.sha256
else
    python -c "import hashlib; import sys; print(hashlib.sha256(open('outputs/metrics.json', 'rb').read()).hexdigest() + '  outputs/metrics.json')" > outputs/metrics.sha256
fi
echo "Checksum saved to outputs/metrics.sha256"

# Verify with audit
echo ""
echo "[4/4] Running audit verification..."
python audit_script.py
echo "Audit complete"

# Display checksum
echo ""
echo "================================================================================"
echo "SUCCESS: Full reproducibility run complete"
echo "================================================================================"
echo ""
echo "Generated outputs:"
echo "  - outputs/metrics.json"
echo "  - outputs/metrics.sha256"
echo "  - outputs/full_metrics.json"
echo "  - outputs/strategy_results.csv"
echo "  - outputs/trades.csv"
echo "  - outputs/benchmark_comparison.csv"
echo "  - outputs/*.png (6 visualizations)"
echo ""
echo "SHA256 checksum:"
cat outputs/metrics.sha256
echo ""
echo "================================================================================"
