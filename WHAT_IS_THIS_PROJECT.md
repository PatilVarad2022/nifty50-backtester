# What Is This Project?

## 🎯 In Simple Terms

This is a **professional trading strategy backtester** for the Indian stock market (NIFTY 50 index). It tests whether simple trading strategies would have made money in the past using real historical data from 2015 to 2025.

Think of it as a "time machine" for trading strategies - you can see how a strategy would have performed over the last 10 years without risking real money.

---

## 💡 What Does It Do?

### 1. **Tests Trading Strategies**
The project implements three professional trading strategies:

- **Momentum Strategy**: Buy when price is above its moving average, sell when below
- **Mean Reversion Strategy**: Buy when price drops below Bollinger Bands, sell when it returns to average
- **RSI Strategy**: Buy when RSI indicates oversold conditions (<30), sell when overbought (>70)

### 2. **Uses Real Market Data**
- Downloads actual NIFTY 50 index data from Yahoo Finance
- Covers 10+ years (2015-2025)
- Automatically updates to include the latest data
- 2,690+ trading days analyzed
- **Includes dividend adjustments** (1.5% annual yield) for realistic benchmark comparison

### 3. **Advanced Risk Management**
- **Stop-Loss**: Automatically exit losing trades at -5% loss
- **Take-Profit**: Lock in gains at +10% profit
- **Position Sizing**: Control how much capital to deploy (50%, 75%, 100%)
- **Transaction Costs**: Realistic 0.1% per trade modeling

### 4. **Calculates Performance Metrics**
Tells you how well each strategy performed:
- **CAGR**: Annual return percentage
- **Sharpe Ratio**: Risk-adjusted returns (higher is better)
- **Sortino Ratio**: Downside risk-adjusted returns
- **Calmar Ratio**: Return vs maximum drawdown
- **Max Drawdown**: Worst loss from peak
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Ratio of wins to losses
- And 15+ other professional metrics

### 5. **Provides Visual Dashboard**
Interactive web dashboard where you can:
- See equity curves (how your money would have grown)
- Analyze risk and drawdowns
- View every single trade with exit reasons (Signal, Stop-Loss, Take-Profit)
- Compare different strategies side-by-side
- Test different parameters
- **Auto-generated insights** explaining performance

---

## 🚀 What Can You Do With It?

### For Learning:
- Understand how trading strategies work
- Learn about risk management and performance metrics
- See the impact of transaction costs
- Practice quantitative analysis

### For Research:
- Test your own strategy ideas
- Compare different approaches
- Analyze performance across market regimes (bull, bear, crash, recovery)
- Validate strategies before risking real money

### For Portfolio Management:
- Understand market behavior over 10 years
- See how strategies perform in different market conditions
- Learn about proper train/test splits to avoid overfitting

---

## 📊 Key Results (2015-2025)

**Best Strategy Found:**
- **Momentum (20-day SMA)**: 29.13% annual return, 1.94 Sharpe ratio
- Beat buy-and-hold by a significant margin
- 138 trades over 10 years
- Max drawdown: -9.90%

**Important Note:** Past performance doesn't guarantee future results. This is for education only.

---

## 🛠️ How It Works

```
1. Download Data → Yahoo Finance (NIFTY 50)
2. Apply Strategy → Generate buy/sell signals
3. Simulate Trades → Execute at next day's open
4. Calculate Returns → Account for transaction costs
5. Analyze Results → Comprehensive metrics
6. Visualize → Interactive dashboard
```

### Execution Model (No Cheating!)
- Signals generated at market close
- Trades execute at next day's open
- No "look-ahead bias" (can't see the future)
- Realistic transaction costs (0.1% per trade)

---

## 📁 What's Inside?

```
Trading_Project/
├── dashboard/          # Interactive web dashboard (Streamlit)
├── src/               # Core backtesting engine
│   ├── backtester.py  # Main strategy simulator
│   ├── metrics.py     # Performance calculations
│   ├── analysis.py    # Advanced analysis tools
│   └── data_loader.py # Data fetching
├── data/              # Market data and results (auto-generated)
├── tests/             # Quality assurance tests
└── README.md          # Technical documentation
```

---

## 🎓 Who Is This For?

✅ **Students** learning quantitative finance  
✅ **Traders** wanting to backtest ideas  
✅ **Analysts** researching market behavior  
✅ **Developers** learning Python for finance  
✅ **Anyone** curious about algorithmic trading  

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the dashboard
streamlit run dashboard/app.py

# 3. Open browser to http://localhost:8501
```

That's it! The dashboard will automatically download the latest data and show you results.

---

## 🔍 What Makes This Professional?

Unlike simple backtests, this project includes:

✅ **Proper execution lag** (no look-ahead bias)  
✅ **Stop-loss & take-profit** (realistic risk management)  
✅ **Position sizing** (fractional capital deployment)  
✅ **Dividend-adjusted returns** (fair benchmark comparison)  
✅ **Transaction costs** (realistic modeling)  
✅ **Train/test splits** (avoid overfitting)  
✅ **Comprehensive metrics** (18+ risk/return measures)  
✅ **Trade-level logging** (every entry/exit with reasons)  
✅ **Auto-generated insights** (AI-powered analysis)  
✅ **Market regime analysis** (performance across different periods)  
✅ **Robust error handling** (graceful edge cases)  
✅ **Unit tests** (quality assurance)  

---

## ⚠️ Important Disclaimers

### This Is:
- ✅ An educational tool
- ✅ A research platform
- ✅ A learning resource

### This Is NOT:
- ❌ Financial advice
- ❌ A guaranteed money-making system
- ❌ A production trading system
- ❌ A recommendation to trade

### Limitations:
- Simplified dividend modeling (1.5% annual yield assumption)
- No taxes modeled
- No slippage beyond transaction costs
- Single asset only (NIFTY 50)
- Daily data only (no intraday)

**Always consult a qualified financial advisor before making investment decisions.**

---

## 📈 Example Output

When you run a backtest, you get:

```
Strategy: Momentum SMA=50
Period: 2015-2025 (2,690 days)

Performance:
- CAGR: 20.77%
- Sharpe Ratio: 1.30
- Max Drawdown: -8.80%
- Total Trades: 80
- Win Rate: 32.5%

vs Buy & Hold:
- Strategy beats benchmark by 8.5% annually
- Lower volatility
- Better risk-adjusted returns
```

Plus detailed charts, trade logs, and regime analysis!

---

## 🤝 Contributing

This is a personal educational project, but suggestions are welcome via GitHub issues.

---

## 📝 License

Educational use only. Use at your own risk.

---

## 🎯 Bottom Line

**This project lets you test trading strategies on 10 years of real NIFTY 50 data to see what would have worked (and what wouldn't) - all without risking a single rupee.**

It's like a flight simulator for traders: practice and learn in a safe environment before attempting the real thing.

---

**Ready to explore?** Run `streamlit run dashboard/app.py` and start analyzing!
