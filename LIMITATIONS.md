# Limitations and Assumptions

## 📋 Overview

This document provides a transparent account of the limitations, assumptions, and simplifications in this backtesting engine. Understanding these constraints is critical for proper interpretation of results and risk-aware decision making.

---

## 🚨 Data Limitations

### 1. **Survivorship Bias**

**Issue**: The NIFTY 50 index composition changes over time. Companies that performed poorly may have been removed from the index, while successful companies were added.

**Impact**: 
- Backtesting on the current NIFTY 50 constituents may overestimate historical performance
- Strategies may appear more profitable than they would have been in real-time
- This is a **known limitation** of using static ticker lists

**Mitigation**:
- We acknowledge this bias explicitly
- Results should be interpreted as "what if we traded the current NIFTY 50 constituents historically"
- For production systems, use point-in-time index composition data

**Data Source**: Yahoo Finance (^NSEI index data)

### 2. **Corporate Actions**

**Not Modeled**:
- Stock splits
- Bonus issues
- Rights issues
- Mergers and acquisitions

**Impact**: Yahoo Finance provides adjusted prices, but complex corporate actions may introduce minor discrepancies.

### 3. **Data Quality**

**Assumptions**:
- OHLC data from Yahoo Finance is accurate
- No missing data handling beyond forward-fill
- Extreme price moves are assumed to be real (not data errors)

**Known Issues**:
- Occasional missing data points (handled via forward-fill)
- Potential data revisions not captured
- Limited to daily frequency (no intraday data)

---

## 💰 Cost and Execution Limitations

### 1. **Transaction Costs**

**Modeled**:
- Flat 0.1% (10 basis points) per trade side
- Applied on position changes only

**Not Modeled**:
- Brokerage fees (varies by broker)
- Exchange fees
- Securities Transaction Tax (STT) in India
- Goods and Services Tax (GST)
- Stamp duty

**Reality Check**: Actual all-in costs for retail traders in India can be 0.15-0.25% per side.

### 2. **Slippage**

**Current Model**: Assumes exact execution at next day's open price

**Not Modeled**:
- Market impact (price moves against you when placing large orders)
- Bid-ask spread
- Partial fills
- Order rejection

**Impact**: Real-world execution will be worse than backtested results, especially for large position sizes.

### 3. **Liquidity Constraints**

**Assumption**: Infinite liquidity at the open price

**Reality**: 
- Large orders may not fill completely at the open
- May need to split orders across multiple days
- NIFTY 50 is highly liquid, so this is less of a concern

### 4. **Execution Timing**

**Model**: 
- Signal generated at close
- Execution at next day's open

**Not Modeled**:
- Intraday execution
- After-hours trading
- Gap risk (overnight price movements)

---

## 📊 Strategy Limitations

### 1. **Position Sizing**

**Current**: 
- Binary positions (0% or 100% invested)
- Optional fractional sizing (50%, 75%, 100%)

**Not Modeled**:
- Dynamic position sizing based on volatility
- Kelly criterion
- Risk parity
- Leverage

### 2. **Risk Management**

**Modeled**:
- Stop-loss (optional, default -5%)
- Take-profit (optional, default +10%)

**Not Modeled**:
- Trailing stops
- Time-based exits
- Volatility-adjusted stops
- Portfolio-level risk limits

### 3. **Rebalancing**

**Current**: Continuous rebalancing (daily signal evaluation)

**Limitation**: 
- No explicit rebalancing frequency control
- No rebalancing cost analysis
- No drift tolerance

### 4. **Market Regimes**

**Regime Detection**: Uses fixed date ranges, not data-driven regime detection

**Limitation**:
- Regimes are subjective and retrospective
- No forward-looking regime prediction
- Regime boundaries are approximate

---

## 💵 Financial Modeling Limitations

### 1. **Dividends**

**Current Model**: 
- Benchmark includes 1.5% annual dividend yield
- Strategy does not earn dividends when out of the market

**Simplification**: 
- Assumes constant dividend yield
- No dividend reinvestment modeling
- No dividend tax

**Impact**: Benchmark returns may be slightly overstated.

### 2. **Taxes**

**Not Modeled**:
- Short-term capital gains tax (STCG)
- Long-term capital gains tax (LTCG)
- Dividend distribution tax
- Tax loss harvesting

**Impact**: After-tax returns will be lower than reported.

### 3. **Financing Costs**

**Not Modeled**:
- Margin interest (if using leverage)
- Opportunity cost of cash
- Collateral requirements

### 4. **Currency Risk**

**Assumption**: All returns in INR (Indian Rupees)

**Not Applicable**: Currency risk only relevant for foreign investors.

---

## 🔬 Methodological Limitations

### 1. **Overfitting Risk**

**Issue**: Parameters optimized on historical data may not work in the future

**Mitigation**:
- Train/test split enforced (2015-2023 train, 2024+ test)
- Parameter selection documented
- Out-of-sample testing encouraged

**Limitation**: Even with train/test split, past performance ≠ future results.

### 2. **Look-Ahead Bias**

**Mitigation**: 
- Proper execution lag (signal at close, execute at next open)
- No future data used in signal generation

**Verified**: Code review and unit tests confirm no look-ahead bias.

### 3. **Statistical Significance**

**Issue**: Limited sample size (10 years, ~2,700 days)

**Impact**:
- Sharpe ratios have wide confidence intervals
- Rare events (crashes) may not be well-represented
- Strategy may not have been tested in all market conditions

### 4. **Benchmark Selection**

**Current**: NIFTY 50 buy-and-hold

**Limitation**:
- No comparison to other strategies
- No comparison to mutual funds or ETFs
- No risk-adjusted benchmark (e.g., 60/40 portfolio)

---

## 🏗️ Technical Limitations

### 1. **Single Asset**

**Current**: NIFTY 50 index only

**Not Supported**:
- Multi-asset portfolios
- Stock-level backtesting
- Sector rotation
- International diversification

### 2. **Data Frequency**

**Current**: Daily OHLC data

**Not Supported**:
- Intraday strategies
- High-frequency trading
- Tick-level data

### 3. **Computational Constraints**

**Current**: Single-threaded Python

**Limitation**:
- No parallel processing
- Limited to small parameter grids
- No GPU acceleration

---

## 🎯 Interpretation Guidelines

### What This Backtester IS:
✅ Educational tool for learning quantitative finance  
✅ Research platform for testing strategy ideas  
✅ Foundation for understanding risk and return  
✅ Demonstration of proper backtesting methodology  

### What This Backtester IS NOT:
❌ Production trading system  
❌ Financial advice  
❌ Guarantee of future performance  
❌ Substitute for professional risk management  

---

## 📈 Recommended Use Cases

### ✅ Appropriate Uses:
- Learning quantitative finance concepts
- Academic research and education
- Strategy prototyping and idea generation
- Understanding historical market behavior
- Comparing different technical indicators

### ❌ Inappropriate Uses:
- Sole basis for investment decisions
- Production trading without further validation
- Claiming guaranteed returns
- Ignoring the limitations listed above

---

## 🔄 Future Improvements

To address these limitations, future versions could include:

1. **Data Enhancements**:
   - Point-in-time index composition
   - Corporate action adjustments
   - Multiple data sources for validation

2. **Cost Modeling**:
   - Realistic all-in transaction costs
   - Slippage models
   - Market impact functions

3. **Risk Management**:
   - Portfolio-level risk limits
   - Dynamic position sizing
   - Multi-asset support

4. **Statistical Rigor**:
   - Bootstrap confidence intervals
   - Monte Carlo simulation
   - Walk-forward analysis

---

## 📝 Conclusion

This backtesting engine is designed for **educational and research purposes**. While it implements many professional-grade features (proper execution lag, transaction costs, comprehensive metrics), it remains a **simplified model** of real-world trading.

**Key Takeaway**: Use this tool to learn, explore, and validate ideas—but always apply additional due diligence, risk management, and professional advice before deploying real capital.

---

**Disclaimer**: Past performance is not indicative of future results. This tool is for educational purposes only. Always consult with a qualified financial advisor before making investment decisions.
