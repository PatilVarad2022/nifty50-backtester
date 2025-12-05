# Quick Reference Guide

## 🚀 Getting Started

### 1. Activate Virtual Environment
```bash
cd d:\Trading_Project
.venv\Scripts\activate
```

### 2. Run the Dashboard
```bash
streamlit run dashboard/app.py
```

### 3. Run Tests
```bash
python tests/test_metrics.py
```

---

## 📊 Key Features at a Glance

### Strategies
- **Momentum (SMA)**: Long when Close > SMA
- **Mean Reversion (Bollinger)**: Buy dips, sell mean reversion

### Top Metrics
- **CAGR**: Compound annual growth rate
- **Sharpe**: Risk-adjusted return (higher = better)
- **Max Drawdown**: Worst peak-to-trough decline
- **Win Rate**: % of profitable trades
- **Profit Factor**: Wins / Losses ratio

---

## 🎯 What's New (Professional Upgrade)

### ✅ Logic Improvements
- Open-to-open returns for both strategy and benchmark
- Transaction costs only on position changes
- Last open position always closed
- Explicit NaN handling (no ghost trades)
- Correct Sortino, Calmar, Profit Factor formulas

### ✅ Engineering
- `.gitignore` added
- `requirements.txt` with version pinning
- 8 unit tests (all passing)
- Graceful error handling

### ✅ UI/UX
- Simplified Overview (top 5 KPIs + expander)
- Visual strategy vs benchmark comparison
- Filterable trade log (by year, by P&L)
- Comprehensive assumptions documentation

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `dashboard/app.py` | Main Streamlit dashboard |
| `src/backtester.py` | Core backtesting engine |
| `src/metrics.py` | Performance metrics |
| `src/analysis.py` | Regime analysis, comparisons |
| `tests/test_metrics.py` | Unit tests |
| `README.md` | Full documentation |
| `IMPLEMENTATION_SUMMARY.md` | Detailed change log |

---

## 🔬 Execution Model

```
Day T (Close):  Signal generated
Day T+1 (Open): Trade executed
```

**Key Points:**
- No look-ahead bias (Position = Signal.shift(1))
- Open-to-open returns for consistency
- Transaction costs: 10 bps per side (default)

---

## 📈 Train/Test Split

- **Train**: 2015-01-01 to 2020-12-31 (parameter tuning)
- **Test**: 2021-01-01 to 2023-12-31 (validation only)

**Rule**: Select parameters on train set, freeze for test set.

---

## 🌍 Market Regimes (Deterministic)

| Regime | Period |
|--------|--------|
| Bull 2015-2017 | 2015-01-01 to 2017-12-31 |
| Correction 2018 | 2018-01-01 to 2018-12-31 |
| Pre-COVID 2019 | 2019-01-01 to 2020-02-29 |
| COVID Crash 2020 | 2020-03-01 to 2020-06-30 |
| Recovery 2020-2021 | 2020-07-01 to 2021-12-31 |
| Post-COVID 2022-2023 | 2022-01-01 to 2023-12-31 |

---

## 🧪 Testing

All tests pass ✅

```bash
python tests/test_metrics.py
```

**Tests Cover:**
- Max drawdown calculation
- Sharpe ratio edge cases
- Sortino with no negative returns
- Calmar with zero drawdown
- Empty trade handling
- Profit factor calculation
- Win rate definitions

---

## ⚠️ Limitations

- No dividends
- No taxes
- No slippage
- No liquidity constraints
- Daily data only
- NIFTY 50 only

---

## 💡 Interview Talking Points

### "How do you avoid look-ahead bias?"
> "Position = Signal.shift(1). Signals at close, execution at next open."

### "Why open-to-open returns?"
> "Consistency. Both strategy and benchmark use same basis for fair comparison."

### "How do you handle transaction costs?"
> "Position change pattern. Costs only when position actually changes."

### "What about edge cases?"
> "Explicit handling. Sortino/Calmar return inf when appropriate, capped for display."

### "How did you define regimes?"
> "Deterministically. Explicit date ranges in code, not data-driven."

### "Train/test split?"
> "2015-2020 train, 2021-2023 test. Parameters selected on train only."

---

## 📞 Quick Help

**Dashboard not loading?**
- Check virtual environment is activated
- Run `pip install -r requirements.txt`

**Tests failing?**
- Ensure all dependencies installed
- Check Python version (3.8+)

**Data loading error?**
- Check internet connection
- Try different date range

---

## 🎓 Next Steps

1. **Explore Dashboard**: Try different strategies and parameters
2. **Review Code**: Read `src/backtester.py` for execution logic
3. **Run Tests**: Understand edge case handling
4. **Read Docs**: Full methodology in `README.md`
5. **Customize**: Add your own strategies or metrics

---

**Status**: ✅ Production-Ready  
**Test Coverage**: 8/8 passing  
**Documentation**: Complete  

For full details, see `README.md` and `IMPLEMENTATION_SUMMARY.md`.
