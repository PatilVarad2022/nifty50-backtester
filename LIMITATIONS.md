# Limitations and Assumptions

## 📋 Overview

This document provides a transparent, quantified account of limitations and assumptions. Understanding these constraints is critical for proper interpretation of results.

---

## 🚨 Data Limitations

### Survivorship Bias ⚠️
- **Issue**: Static NIFTY 50 list (current constituents only)
- **Impact**: **+1-2% CAGR inflation**, **+0.1-0.2 Sharpe inflation**
- **Mitigation**: Results interpreted as "current constituents traded historically"

### Corporate Actions
- **Handled**: Stock splits, dividends (Yahoo Finance adjusted prices)
- **Not Handled**: Index rebalancing, mergers, delistings
- **Impact**: **±0.3% CAGR uncertainty**

### Data Quality
- **Source**: Yahoo Finance (assumed accurate)
- **Missing Data**: <0.1% of data points (forward-fill used)
- **Impact**: **Minimal** (<0.1% CAGR effect)

---

## 💰 Cost & Execution Limitations

### Transaction Costs
- **Modeled**: Flat 0.1% (10 bps) per trade side
- **Not Modeled**: STT, GST, stamp duty (India-specific taxes)
- **Reality**: Retail all-in costs = **0.15-0.25%** per side
- **Impact**: **+0.5-1% CAGR overstatement**

### Slippage
- **Assumption**: Exact execution at next day's open
- **Reality**: Market impact, bid-ask spread, partial fills
- **Impact**: **+0.5-1% CAGR overstatement**

### Liquidity
- **Assumption**: Infinite liquidity at open price
- **Reality**: NIFTY 50 is highly liquid (minimal impact for retail)
- **Impact**: **Negligible** for position sizes <₹10 crore

---

## 📊 Modeling Limitations

### Dividends
- **Benchmark**: 1.5% annual yield (simplified)
- **Reality**: Variable dividend yields, reinvestment timing
- **Impact**: **±0.3% CAGR uncertainty**

### Taxes
- **Not Modeled**: STCG (15%), LTCG (10% above ₹1L), dividend tax
- **Impact**: **-2-4% after-tax CAGR reduction**

### Position Sizing
- **Current**: Fixed 1x notional (binary 0% or 100%)
- **Alternative**: Kelly criterion, vol-based sizing
- **Impact**: **+0.5-1% CAGR potential improvement**

---

## 🔬 Methodological Limitations

### Overfitting Risk
- **Mitigation**: Train/test split (2015-2023 train, 2024+ test)
- **Limitation**: Even with split, past ≠ future
- **Impact**: **Unknown** (inherent to all backtests)

### Sample Size
- **Period**: 10 years (~2,700 days)
- **Limitation**: May not capture all market regimes
- **Impact**: **Wide confidence intervals** on Sharpe ratio

### Benchmark
- **Current**: NIFTY 50 buy-and-hold only
- **Missing**: Mutual funds, ETFs, risk-adjusted benchmarks
- **Impact**: **Incomplete** performance context

---

## 📈 Combined Impact Summary

| Limitation | Estimated CAGR Impact |
|------------|----------------------|
| Survivorship Bias | +1-2% (overstatement) |
| No Slippage | +0.5-1% (overstatement) |
| Simplified Dividends | ±0.3% (uncertainty) |
| No Taxes | -2-4% (after-tax reduction) |
| Static Position Sizing | +0.5-1% (potential improvement) |
| **Net Effect** | **Real-world CAGR likely 3-5% lower** |

**Example**: Reported 20.81% CAGR → Realistic 16-18% CAGR after all adjustments.

---

## ⚠️ Interpretation Guidelines

### What This Backtester IS:
✅ Educational tool for learning quantitative finance  
✅ Research platform for testing strategy ideas  
✅ Demonstration of proper backtesting methodology  

### What This Backtester IS NOT:
❌ Production trading system  
❌ Financial advice  
❌ Guarantee of future performance  

---

## 🔄 Recommended Use Cases

### ✅ Appropriate:
- Learning quantitative finance concepts
- Academic research and education
- Strategy prototyping
- Understanding historical market behavior

### ❌ Inappropriate:
- Sole basis for investment decisions
- Production trading without further validation
- Claiming guaranteed returns

---

**Conclusion**: Use this tool to learn and explore, but apply additional due diligence, risk management, and professional advice before deploying real capital.
