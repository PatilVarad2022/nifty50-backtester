# Strategy Rationale & Economic Intuition

## 🎯 Purpose

This document explains **why** the implemented trading strategies might work, grounded in financial theory and market microstructure. Understanding the economic rationale is critical for:

1. **Recruiter Evaluation**: Demonstrates financial reasoning, not just coding
2. **Risk Awareness**: Knowing when strategies might fail
3. **Parameter Selection**: Justifying choices beyond curve-fitting

---

## 📈 Strategy 1: Momentum (Simple Moving Average)

### Economic Intuition

**Core Hypothesis**: "The trend is your friend" — assets that have been rising tend to continue rising in the short-to-medium term.

**Why Momentum Works**:

1. **Behavioral Finance**:
   - **Herding**: Investors follow the crowd, creating self-reinforcing trends
   - **Anchoring**: Investors anchor to recent prices, slow to update beliefs
   - **Disposition Effect**: Winners are held too long, losers sold too late

2. **Risk-Seeking Capital**:
   - Capital flows into assets showing strength
   - Positive feedback loop: rising prices → more buyers → higher prices
   - Momentum = proxy for capital inflows

3. **Information Diffusion**:
   - Good news takes time to be fully priced in
   - Analysts revise earnings estimates gradually
   - Momentum captures this slow information absorption

4. **Institutional Flows**:
   - Mutual funds and institutions execute large orders over days/weeks
   - Their buying creates sustained price pressure

**Academic Support**:
- Jegadeesh & Titman (1993): Momentum profits persist for 3-12 months
- Asness et al. (2013): Momentum works across asset classes and geographies
- Fama-French: Momentum is a documented risk factor

### When Momentum Fails

❌ **Regime Changes**: Sharp reversals (e.g., COVID crash March 2020)  
❌ **Mean Reversion Periods**: Choppy, range-bound markets  
❌ **Transaction Costs**: High turnover erodes profits  
❌ **Crowding**: When everyone uses momentum, it stops working  

### Parameter Justification

**Why 50-day SMA?**

- **20-day**: Too sensitive, generates excessive trades (high costs)
- **50-day**: Balances signal quality and turnover (~2 months of data)
- **200-day**: Too slow, misses intermediate trends

**Empirical Evidence** (from our backtest):
- 20-day SMA: Higher CAGR but lower Sharpe (more whipsaws)
- 50-day SMA: **Best risk-adjusted returns** (Sharpe 1.31)
- 200-day SMA: Lower returns, fewer trades

**Conclusion**: 50-day SMA is a **sweet spot** between signal quality and transaction costs.

---

## 🔄 Strategy 2: Mean Reversion (Bollinger Bands)

### Economic Intuition

**Core Hypothesis**: "What goes up must come down" — prices that deviate significantly from their average tend to revert.

**Why Mean Reversion Works**:

1. **Overreaction Hypothesis**:
   - Investors overreact to news (both good and bad)
   - Prices overshoot fundamental value
   - Reversion = correction of overreaction

2. **Liquidity Provision**:
   - Mean reversion strategies provide liquidity to panicked sellers
   - Earn a premium for taking the other side of emotional trades

3. **Market Microstructure**:
   - Temporary supply/demand imbalances create price dislocations
   - Informed traders arbitrage these away
   - Mean reversion captures this arbitrage

4. **Statistical Properties**:
   - Many financial time series are stationary (mean-reverting) over long horizons
   - Bollinger Bands identify statistical extremes (2 standard deviations)

**Academic Support**:
- DeBondt & Thaler (1985): Long-term overreaction and reversal
- Jegadeesh (1990): Short-term reversal (1-month)
- Lo & MacKinlay (1988): Contrarian profits

### When Mean Reversion Fails

❌ **Strong Trends**: Prices can stay "extreme" for extended periods  
❌ **Structural Breaks**: Fundamental regime changes (not temporary)  
❌ **Low Volatility**: Narrow bands = fewer signals  
❌ **Black Swans**: Extreme events don't revert quickly  

### Parameter Justification

**Why 20-day SMA + 2 Std Dev?**

- **20-day**: Short enough to capture temporary dislocations
- **2 Std Dev**: Standard statistical threshold (95% confidence)
- **Alternative**: 1 Std Dev = too many signals, 3 Std Dev = too few

**Empirical Evidence**:
- Bollinger himself recommends 20-day, 2 Std Dev as default
- Our backtest shows this captures ~15-20 mean reversion opportunities per year

---

## 📊 Strategy 3: RSI (Relative Strength Index)

### Economic Intuition

**Core Hypothesis**: "Overbought" and "oversold" conditions signal temporary extremes that will reverse.

**Why RSI Works**:

1. **Momentum Exhaustion**:
   - RSI measures the speed and magnitude of price changes
   - Extreme RSI = momentum is overextended
   - Likely to pause or reverse

2. **Sentiment Extremes**:
   - RSI < 30: Fear dominates, sellers exhausted
   - RSI > 70: Greed dominates, buyers exhausted
   - Contrarian entry at extremes

3. **Oscillator Properties**:
   - RSI is bounded (0-100), unlike price
   - Easier to identify "extreme" levels
   - Divergences signal weakening trends

**Academic Support**:
- Wilder (1978): Original RSI paper
- Brock et al. (1992): Technical trading rules have predictive power
- Park & Irwin (2007): Meta-analysis shows modest profitability

### When RSI Fails

❌ **Strong Trends**: RSI can stay overbought/oversold for weeks  
❌ **Low Volatility**: RSI oscillates in middle range (no signals)  
❌ **Whipsaws**: False signals in choppy markets  

### Parameter Justification

**Why 14-day RSI with 30/70 thresholds?**

- **14-day**: Wilder's original recommendation (2 weeks of data)
- **30/70**: Standard thresholds (not 20/80 which is too extreme)
- **Alternative**: 9-day RSI = more sensitive, 21-day = smoother

**Empirical Evidence**:
- 14-day is industry standard
- 30/70 thresholds balance signal frequency and quality

---

## 🏦 Portfolio Manager Insights

### What a PM Would Care About

1. **Risk-Adjusted Returns**:
   - Sharpe ratio > 1.0 is excellent for a single-asset strategy
   - Max drawdown < 10% is acceptable for equity strategies

2. **Strategy Diversification**:
   - Momentum and mean reversion are **negatively correlated**
   - Combining them reduces portfolio volatility

3. **Capacity**:
   - NIFTY 50 is highly liquid (can deploy large capital)
   - Strategy turnover is moderate (not HFT)

4. **Regime Awareness**:
   - Momentum works in trending markets (2015-2017, 2020-2021)
   - Mean reversion works in range-bound markets (2018, 2022)

5. **Implementation Feasibility**:
   - Simple rules = easy to implement
   - No complex data requirements
   - Robust to minor execution errors

---

## 🔬 Why These Strategies, Not Others?

### Strategies We Chose:
✅ **Momentum**: Proven, robust, works across markets  
✅ **Mean Reversion**: Diversifying, exploits overreaction  
✅ **RSI**: Simple, interpretable, widely used  

### Strategies We Didn't Implement (and Why):

❌ **Machine Learning**: 
- Requires more data
- Overfitting risk
- Hard to explain to stakeholders

❌ **Fundamental Analysis**:
- NIFTY 50 is an index (no fundamentals)
- Would need stock-level data

❌ **High-Frequency**:
- Requires tick data
- Infrastructure-intensive
- Not suitable for retail

❌ **Options Strategies**:
- Requires options data
- More complex risk management
- Beyond scope of this project

---

## 📚 References

1. **Jegadeesh, N., & Titman, S. (1993)**. "Returns to Buying Winners and Selling Losers." *Journal of Finance*.

2. **DeBondt, W., & Thaler, R. (1985)**. "Does the Stock Market Overreact?" *Journal of Finance*.

3. **Brock, W., Lakonishok, J., & LeBaron, B. (1992)**. "Simple Technical Trading Rules." *Journal of Finance*.

4. **Asness, C., Moskowitz, T., & Pedersen, L. (2013)**. "Value and Momentum Everywhere." *Journal of Finance*.

5. **Wilder, J. W. (1978)**. *New Concepts in Technical Trading Systems*. Trend Research.

---

## 🎯 Conclusion

These strategies are **not magic**. They work because they exploit well-documented behavioral biases and market microstructure effects. However, they:

- **Are not guaranteed** to work in the future
- **Require discipline** to execute (no emotional overrides)
- **Have periods of underperformance** (drawdowns are normal)
- **Work best in combination** (diversification)

**Key Takeaway**: Understanding *why* a strategy works is as important as *how* to implement it. This knowledge helps you:
- Stick with the strategy during drawdowns
- Recognize when market conditions have changed
- Adapt parameters intelligently (not curve-fit)

---

**For Recruiters**: This document demonstrates that I understand not just the code, but the **financial theory** behind it. I can explain strategies to non-technical stakeholders and make risk-aware decisions.
