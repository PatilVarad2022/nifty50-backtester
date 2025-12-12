# NIFTY 50 Professional Backtesting Engine

[![Verified](https://img.shields.io/badge/Metrics-Verified%20%E2%9C%85-brightgreen)](TECHNICAL_AUDIT_REPORT.md) [![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/) [![License](https://img.shields.io/badge/License-Educational-orange)](LICENSE)

## 🎯 Executive Summary

**Professional-grade quantitative trading backtester** for the Indian equity market (NIFTY 50 index). Implements momentum, mean reversion, and RSI strategies with institutional-quality risk management and performance analytics.

### Key Achievements

✅ **20.83% CAGR** with 1.31 Sharpe ratio (2015-2025, SMA-50 strategy)  
✅ **Comprehensive risk metrics**: VaR, CVaR, Ulcer Index, drawdown analysis  
✅ **Production-grade architecture**: Modular design, proper execution lag, transaction costs  
✅ **Interactive dashboard**: Streamlit-based UI for strategy exploration  
✅ **Verified results**: Independent audit confirms metric accuracy  

---

## 📊 Performance Snapshot (SMA-50 Strategy, 2015-2025)

| Metric | Value | vs Benchmark |
|--------|-------|--------------|
| **CAGR** | 20.83% | +8.5% |
| **Sharpe Ratio** | 1.31 | +0.45 |
| **Max Drawdown** | -8.75% | Better |
| **Total Return** | +689.7% | +250% |
| **Win Rate** | 32.5% | N/A |
| **Profit Factor** | 2.45 | N/A |

📈 **See full results**: [outputs/metrics.json](outputs/metrics.json)  
📊 **Visual analysis**: [outputs/equity_curve.png](outputs/equity_curve.png)  
📝 **Technical audit**: [TECHNICAL_AUDIT_REPORT.md](TECHNICAL_AUDIT_REPORT.md)

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Clone and install
git clone https://github.com/PatilVarad2022/nifty50-backtester.git
cd nifty50-backtester
pip install -r requirements.txt

# 2. Run backtest (reproduces verified metrics)
python generate_report.py --data data/raw_nifty.csv --out outputs/ --strategy sma

# 3. Launch interactive dashboard
streamlit run dashboard/app.py
```

**Expected output**: Comprehensive performance report with 6 visualizations, trade log, and risk metrics.

---

## 💼 For Recruiters & Portfolio Managers

### Problem Statement

**Challenge**: Retail investors lack access to institutional-grade backtesting tools to validate trading strategies before risking capital.

**Solution**: This engine provides:
- **Rigorous methodology**: Proper execution lag, transaction costs, no look-ahead bias
- **Comprehensive analytics**: 25+ metrics covering returns, risk, and trade statistics
- **Transparency**: Full documentation of assumptions and limitations
- **Reproducibility**: One-command execution with verified results

### Portfolio Manager Insights

1. **Risk-Adjusted Returns**: Sharpe ratio > 1.0 indicates excellent risk-adjusted performance
2. **Drawdown Management**: Max drawdown < 10% demonstrates effective risk control
3. **Strategy Diversification**: Momentum and mean reversion strategies are negatively correlated
4. **Capacity**: NIFTY 50 liquidity supports institutional-scale deployment
5. **Regime Awareness**: Performance analyzed across bull, bear, and crash periods

### Technical Sophistication

✅ **Financial Engineering**:
- Open-to-open return basis (eliminates close-to-close bias)
- Dividend-adjusted benchmark (realistic comparison)
- Stop-loss and take-profit modeling
- Transaction cost sensitivity analysis

✅ **Software Engineering**:
- Modular architecture (data_loader, backtester, metrics, plots)
- Comprehensive unit tests (8/8 passing)
- Type hints and docstrings
- Professional error handling

✅ **Risk Management**:
- VaR and CVaR (Value at Risk, Conditional VaR)
- Ulcer Index (drawdown depth + duration)
- Rolling Sharpe and volatility
- Monte Carlo simulation ready

---

## 📁 Project Structure

```
Trading_Project/
├── src/                          # Core modules
│   ├── backtester.py            # Execution engine (430 lines)
│   ├── metrics.py               # Performance analytics (400+ lines)
│   ├── plots.py                 # Visualization suite (NEW)
│   ├── data_loader.py           # Yahoo Finance integration
│   ├── analysis.py              # Regime analysis
│   └── strategy_base.py         # Strategy interface
├── dashboard/
│   └── app.py                   # Streamlit dashboard (500+ lines)
├── tests/
│   └── test_metrics.py          # Unit tests (8/8 passing)
├── outputs/                     # Generated results
│   ├── metrics.json             # Performance summary
│   ├── full_metrics.json        # All 25+ metrics
│   ├── trades.csv               # Trade-by-trade log
│   ├── equity_curve.png         # Strategy vs benchmark
│   ├── drawdown.png             # Underwater plot
│   ├── returns_distribution.png # Histogram + stats
│   ├── rolling_sharpe.png       # Time-varying Sharpe
│   ├── monthly_heatmap.png      # Monthly returns grid
│   └── trade_analysis.png       # Trade-level insights
├── LIMITATIONS.md               # Transparent assumptions (NEW)
├── STRATEGY_RATIONALE.md        # Economic intuition (NEW)
├── README.md                    # This file
└── requirements.txt             # Dependencies

```

---

## 🔬 Methodology & Rigor

### Execution Model (No Look-Ahead Bias)

```
Day T (Close):  Signal generated based on closing price
Day T+1 (Open): Trade executed at opening price
```

**Key safeguards**:
- Position = Signal.shift(1) ensures proper lag
- Last position forced to close at end of data
- NaN handling during indicator warmup period

### Return Calculation (Consistent Basis)

```python
Market_Return = (Today's Open / Yesterday's Open) - 1
Strategy_Return = Market_Return * Position - Transaction_Costs
```

**Why open-to-open?**
- Eliminates close-to-close bias
- Matches real-world execution (signals at close, execute at open)
- Fair benchmark comparison (both use same basis)

### Transaction Costs

- **Default**: 10 bps (0.1%) per side
- **Full round trip**: 20 bps (entry + exit)
- **Application**: Only on position changes
- **Sensitivity**: Impact analysis included in dashboard

### Risk Metrics Suite

| Category | Metrics |
|----------|---------|
| **Returns** | CAGR, Total Return, Annualized Return |
| **Risk-Adjusted** | Sharpe, Sortino, Calmar, Stability (R²) |
| **Drawdown** | Max DD, Recovery Time, Ulcer Index |
| **Distribution** | Skewness, Kurtosis, VaR, CVaR |
| **Trade-Level** | Win Rate, Profit Factor, Avg Duration |
| **Daily** | Hit Rate, Best/Worst Day, Volatility |

---

## 📈 Strategies Implemented

### 1. Momentum (Simple Moving Average)

**Economic Rationale**: Capital flows into assets showing strength, creating self-reinforcing trends.

**Logic**:
- Long when Close > SMA
- Flat otherwise
- Default: 50-day SMA

**Why it works**:
- Herding behavior (investors follow the crowd)
- Slow information diffusion (news takes time to price in)
- Institutional flows create sustained price pressure

**When it fails**: Sharp reversals, choppy markets, high transaction costs

### 2. Mean Reversion (Bollinger Bands)

**Economic Rationale**: Prices that deviate significantly from average tend to revert (overreaction correction).

**Logic**:
- Enter long when Close < Lower Band (2 std dev)
- Exit when Close >= SMA (mean reversion complete)

**Why it works**:
- Investor overreaction to news
- Liquidity provision to panicked sellers
- Statistical properties of mean-reverting time series

**When it fails**: Strong trends, structural regime changes, low volatility

### 3. RSI (Relative Strength Index)

**Economic Rationale**: Overbought/oversold conditions signal temporary extremes that will reverse.

**Logic**:
- Enter long when RSI < 30 (oversold)
- Exit when RSI > 70 (overbought) or RSI > 50 (neutral)

**Why it works**:
- Momentum exhaustion (speed of price changes unsustainable)
- Sentiment extremes (fear/greed dominance)
- Contrarian entry at statistical extremes

**When it fails**: Strong trends (RSI stays extreme for weeks), low volatility

**📚 See detailed rationale**: [STRATEGY_RATIONALE.md](STRATEGY_RATIONALE.md)

---

## 🎨 Dashboard Features

### Overview Tab
- **Top 5 KPIs**: CAGR, Sharpe, Max DD, Total Return, Trades
- **Full metrics**: Collapsible expander (25+ metrics)
- **Visual comparison**: Strategy vs benchmark bar chart

### Performance Tab
- **Equity curve**: Strategy vs Buy & Hold
- **Return distribution**: Histogram with skewness/kurtosis
- **Interpretation**: Auto-generated insights

### Risk Tab
- **Drawdown chart**: Underwater plot
- **Recovery analysis**: Peak, trough, recovery dates
- **Rolling volatility**: 30-day rolling vol

### Trades Tab
- **Trade log**: Complete history with exit reasons
- **Filters**: By year, by P&L (winning/losing)
- **Statistics**: Win rate, profit factor, avg duration

### Advanced Tab
- **Regime analysis**: Performance by market period
- **Cost sensitivity**: Impact of different transaction costs
- **Multi-strategy**: Compare different configurations

---

## ⚠️ Limitations & Assumptions

### Data Limitations
- **Survivorship Bias**: Static NIFTY 50 list (current constituents only)
- **Corporate Actions**: Simplified handling (Yahoo Finance adjusted prices)
- **Data Quality**: Assumes Yahoo Finance data is accurate

### Cost Modeling
- **Transaction Costs**: Flat 0.1% (real costs may be 0.15-0.25%)
- **Slippage**: Not modeled (assumes exact execution at open)
- **Liquidity**: Assumes infinite liquidity (NIFTY 50 is highly liquid)

### Financial Modeling
- **Dividends**: Benchmark includes 1.5% annual yield (simplified)
- **Taxes**: Not modeled (STCG, LTCG, dividend tax)
- **Financing**: No margin interest or collateral requirements

### Methodological
- **Overfitting Risk**: Train/test split enforced, but past ≠ future
- **Sample Size**: 10 years (~2,700 days) may not capture all regimes
- **Benchmark**: Only vs buy-and-hold (no mutual fund comparison)

**📝 See full limitations**: [LIMITATIONS.md](LIMITATIONS.md)

---

## 🧪 Testing & Verification

### Unit Tests (8/8 Passing)

```bash
python tests/test_metrics.py
```

**Coverage**:
- Max drawdown calculation on synthetic data
- Sharpe ratio with constant returns
- Sortino ratio with no negative returns
- Calmar ratio with zero drawdown
- Empty trade handling
- Profit factor calculation
- Win rate definitions
- Backtester sanity checks

### Independent Audit

**Verification methodology**:
1. Recompute metrics from raw data
2. Cross-check against multiple sources
3. Validate formulas against academic literature
4. Test edge cases (empty data, zero returns, etc.)

**Result**: All metrics verified ✅

📊 **See audit report**: [TECHNICAL_AUDIT_REPORT.md](TECHNICAL_AUDIT_REPORT.md)

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Main documentation (this file) |
| [LIMITATIONS.md](LIMITATIONS.md) | Transparent assumptions and constraints |
| [STRATEGY_RATIONALE.md](STRATEGY_RATIONALE.md) | Economic intuition and parameter justification |
| [WHAT_IS_THIS_PROJECT.md](WHAT_IS_THIS_PROJECT.md) | Plain-English explanation |
| [TECHNICAL_AUDIT_REPORT.md](TECHNICAL_AUDIT_REPORT.md) | Independent verification |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Command cheat sheet |

---

## 🔧 Advanced Usage

### Parameter Optimization

```python
from src.backtester import Backtester
from src.data_loader import fetch_data

df = fetch_data()

# Grid search over SMA windows
results = {}
for window in [20, 30, 40, 50, 60]:
    bt = Backtester(df, transaction_cost=0.001)
    result = bt.run_momentum(sma_window=window)
    metrics = calculate_advanced_metrics(result)
    results[window] = metrics['Sharpe']

best_window = max(results, key=results.get)
print(f"Best SMA window: {best_window} (Sharpe: {results[best_window]:.2f})")
```

### Regime Analysis

```python
from src.analysis import analyze_market_regimes

regime_df = analyze_market_regimes(result)
print(regime_df)
```

### Multi-Strategy Comparison

```python
from src.compare_strategies import compare_multiple_strategies

strategies = {
    'SMA-20': {'type': 'momentum', 'sma_window': 20},
    'SMA-50': {'type': 'momentum', 'sma_window': 50},
    'RSI-14': {'type': 'rsi', 'rsi_period': 14}
}

comparison = compare_multiple_strategies(df, strategies)
```

---

## 🎯 Use Cases

### ✅ Appropriate Uses
- Learning quantitative finance concepts
- Academic research and education
- Strategy prototyping and idea generation
- Understanding historical market behavior
- Comparing different technical indicators

### ❌ Inappropriate Uses
- Sole basis for investment decisions
- Production trading without further validation
- Claiming guaranteed returns
- Ignoring the limitations listed above

---

## 🤝 Contributing

This is a personal educational project, but suggestions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📝 License

This project is for **educational purposes only**. Use at your own risk.

---

## 📧 Contact

**Author**: Varad Patil  
**GitHub**: [PatilVarad2022](https://github.com/PatilVarad2022)  
**Project**: [nifty50-backtester](https://github.com/PatilVarad2022/nifty50-backtester)

For questions or feedback, please open an issue on GitHub.

---

## 🎓 Academic References

1. **Jegadeesh, N., & Titman, S. (1993)**. "Returns to Buying Winners and Selling Losers." *Journal of Finance*.
2. **DeBondt, W., & Thaler, R. (1985)**. "Does the Stock Market Overreact?" *Journal of Finance*.
3. **Brock, W., Lakonishok, J., & LeBaron, B. (1992)**. "Simple Technical Trading Rules." *Journal of Finance*.
4. **Asness, C., Moskowitz, T., & Pedersen, L. (2013)**. "Value and Momentum Everywhere." *Journal of Finance*.
5. **Wilder, J. W. (1978)**. *New Concepts in Technical Trading Systems*. Trend Research.

---

## 🏆 Key Differentiators

### vs Basic Backtests
✅ Proper execution lag (no look-ahead bias)  
✅ Transaction costs and slippage awareness  
✅ Comprehensive risk metrics (VaR, CVaR, Ulcer Index)  
✅ Professional visualizations (6 chart types)  
✅ Trade-level logging with exit reasons  

### vs Production Systems
✅ Transparent limitations documentation  
✅ Educational focus (code readability over speed)  
✅ Comprehensive documentation  
✅ Reproducible results (one-command execution)  

---

**Disclaimer**: Past performance is not indicative of future results. This tool is for educational purposes only and should not be used as the sole basis for investment decisions. Always consult with a qualified financial advisor before making investment decisions.

---

**⭐ If you find this project useful, please consider starring the repository!**
