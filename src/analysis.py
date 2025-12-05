"""
Professional analysis module for backtesting.

IMPORTANT - Train/Test Split Discipline:
- Train Period: 2015-01-01 to 2023-12-31 (parameter selection, grid search)
- Test Period: 2024-01-01 onwards (validation only, parameters frozen)

All parameter tuning (SMA windows, Bollinger Band widths, etc.) MUST be done
on the train set only. The test set is strictly for out-of-sample validation.

If you claim "out-of-sample" results, you must have selected parameters using
only the train set. Otherwise, it's in-sample overfitting.
"""

import pandas as pd
import numpy as np
from backtester import Backtester
from metrics import calculate_advanced_metrics, calculate_trade_metrics


def split_data(df, train_end='2023-12-31'):
    """
    Split data into in-sample (train) and out-of-sample (test).
    
    CRITICAL: Use this for proper parameter selection workflow:
    1. Run grid search on train set only
    2. Select best parameters based on train metrics
    3. Freeze parameters
    4. Evaluate on test set for true out-of-sample performance
    
    Args:
        df: Full dataset
        train_end: Last date of training period (default: 2023-12-31)
    
    Returns:
        train_df, test_df (both DataFrames)
    """
    train = df[df.index <= train_end].copy()
    test = df[df.index > train_end].copy()
    
    print(f"Train set: {train.index[0]} to {train.index[-1]} ({len(train)} days)")
    print(f"Test set: {test.index[0]} to {test.index[-1]} ({len(test)} days)")
    
    return train, test

def compare_with_benchmark(strategy_df, initial_capital=100000):
    """
    Calculate Buy & Hold metrics for comparison.
    
    Returns:
        Dict of benchmark metrics
    """
    market_ret = strategy_df['Market_Return'].dropna()
    
    if len(market_ret) == 0:
        return {}
    
    days = (strategy_df.index[-1] - strategy_df.index[0]).days
    total_return = (strategy_df['Market_Equity'].iloc[-1] / strategy_df['Market_Equity'].iloc[0]) - 1
    cagr = (1 + total_return) ** (365.0 / days) - 1
    
    volatility = market_ret.std() * np.sqrt(252)
    sharpe = (market_ret.mean() * 252 - 0.06) / volatility if volatility != 0 else 0
    
    # Drawdown
    cum_ret = (1 + market_ret).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    max_dd = drawdown.min()
    
    return {
        "Strategy": "Buy & Hold",
        "CAGR": cagr,
        "Sharpe": sharpe,
        "Max_Drawdown": max_dd,
        "Volatility": volatility,
        "Total_Return": total_return
    }

def analyze_market_regimes(df):
    """
    Break down performance by deterministic market regimes.
    
    DETERMINISTIC REGIME DEFINITIONS:
    These date ranges are explicitly defined, not data-driven.
    If asked "how did you define regimes?", point to these exact ranges.
    
    Regimes:
    - Bull 2015-2017: Strong uptrend period
    - Correction 2018: Market correction year
    - Pre-COVID 2019: Recovery before pandemic
    - COVID Crash 2020: March-June 2020 crash
    - Recovery 2020-2021: Post-COVID recovery
    - Post-COVID 2022-2023: Normalized market
    
    Args:
        df: DataFrame with Strategy_Return and Strategy_Equity columns
        
    Returns:
        DataFrame with regime-wise performance metrics
    """
    # EXPLICIT REGIME DATE RANGES - Deterministic, not data-driven
    regimes = {
        "Bull 2015-2017": ("2015-01-01", "2017-12-31"),
        "Correction 2018": ("2018-01-01", "2018-12-31"),
        "Pre-COVID 2019": ("2019-01-01", "2020-02-29"),
        "COVID Crash 2020": ("2020-03-01", "2020-06-30"),
        "Recovery 2020-2021": ("2020-07-01", "2021-12-31"),
        "Post-COVID 2022-2023": ("2022-01-01", "2023-12-31"),
        "Recent 2024-2025": ("2024-01-01", "2025-12-31")
    }
    
    results = []
    
    for regime_name, (start, end) in regimes.items():
        regime_df = df[(df.index >= start) & (df.index <= end)]
        
        if len(regime_df) == 0:
            continue
        
        strat_ret = regime_df['Strategy_Return'].dropna()
        if len(strat_ret) == 0:
            continue
        
        total_ret = (regime_df['Strategy_Equity'].iloc[-1] / regime_df['Strategy_Equity'].iloc[0]) - 1
        
        results.append({
            "Regime": regime_name,
            "Start": start,
            "End": end,
            "Total_Return": total_ret,
            "Avg_Daily_Return": strat_ret.mean(),
            "Volatility": strat_ret.std() * np.sqrt(252)
        })
    
    return pd.DataFrame(results)

def transaction_cost_sensitivity(data, strategy_func, params, costs=[0.0005, 0.001, 0.002]):
    """
    Test strategy performance across different transaction costs.
    
    Args:
        data: Market data
        strategy_func: Function to run (e.g., bt.run_momentum)
        params: Dict of strategy parameters
        costs: List of transaction costs to test
    
    Returns:
        DataFrame with results
    """
    results = []
    
    for cost in costs:
        bt = Backtester(data, transaction_cost=cost)
        
        # Run strategy based on parameters
        if 'rsi_period' in params:
            res_df = bt.run_rsi(**params)
        elif 'sma_window' in params and 'std_dev' not in params:
            res_df = bt.run_momentum(**params)
        else:
            res_df = bt.run_mean_reversion(**params)
        
        metrics = calculate_advanced_metrics(res_df)
        
        results.append({
            "Transaction_Cost_bps": cost * 10000,
            "CAGR": metrics['CAGR'],
            "Sharpe": metrics['Sharpe'],
            "Max_Drawdown": metrics['Max_Drawdown']
        })
    
    return pd.DataFrame(results)

def multi_strategy_comparison(data):
    """
    Compare multiple strategy configurations.
    
    Returns:
        DataFrame with all configurations
    """
    configs = [
        ("Momentum", {"sma_window": 20}),
        ("Momentum", {"sma_window": 50}),
        ("Momentum", {"sma_window": 100}),
        ("Momentum", {"sma_window": 200}),
        ("Mean Reversion", {"sma_window": 20, "std_dev": 1.5}),
        ("Mean Reversion", {"sma_window": 20, "std_dev": 2.0}),
        ("Mean Reversion", {"sma_window": 20, "std_dev": 2.5}),
        ("RSI", {"rsi_period": 14, "oversold": 30, "overbought": 70}),
        ("RSI", {"rsi_period": 14, "oversold": 25, "overbought": 75}),
        ("RSI", {"rsi_period": 21, "oversold": 30, "overbought": 70}),
    ]
    
    results = []
    
    for strategy_name, params in configs:
        bt = Backtester(data)
        
        if strategy_name == "Momentum":
            res_df = bt.run_momentum(**params)
            param_str = f"SMA={params['sma_window']}"
        elif strategy_name == "Mean Reversion":
            res_df = bt.run_mean_reversion(**params)
            param_str = f"SMA={params['sma_window']}, BB={params['std_dev']}"
        else:  # RSI
            res_df = bt.run_rsi(**params)
            param_str = f"Period={params['rsi_period']}, OS={params['oversold']}, OB={params['overbought']}"
        
        metrics = calculate_advanced_metrics(res_df)
        trade_metrics = calculate_trade_metrics(bt.trades)
        
        results.append({
            "Strategy": strategy_name,
            "Parameters": param_str,
            "CAGR": metrics['CAGR'],
            "Sharpe": metrics['Sharpe'],
            "Sortino": metrics['Sortino'],
            "Calmar": metrics['Calmar'],
            "Max_Drawdown": metrics['Max_Drawdown'],
            "Total_Trades": trade_metrics['Total_Trades'],
            "Win_Rate": trade_metrics['Win_Rate_Trade']
        })
    
    return pd.DataFrame(results)


def calculate_monthly_returns(df):
    """
    Calculate monthly returns for heatmap visualization.
    
    Args:
        df: DataFrame with Strategy_Return column
        
    Returns:
        DataFrame with years as rows, months as columns
    """
    monthly_data = df['Strategy_Return'].resample('M').apply(lambda x: (1 + x).prod() - 1)
    monthly_data = monthly_data * 100  # Convert to percentage
    
    # Create pivot table
    monthly_pivot = pd.DataFrame({
        'Year': monthly_data.index.year,
        'Month': monthly_data.index.month,
        'Return': monthly_data.values
    })
    
    heatmap_data = monthly_pivot.pivot(index='Year', columns='Month', values='Return')
    heatmap_data.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    return heatmap_data


def calculate_annual_returns(df):
    """
    Calculate year-by-year returns.
    
    Args:
        df: DataFrame with Strategy_Return and Market_Return columns
        
    Returns:
        DataFrame with annual performance
    """
    annual_strategy = df['Strategy_Return'].resample('Y').apply(lambda x: (1 + x).prod() - 1)
    annual_market = df['Market_Return'].resample('Y').apply(lambda x: (1 + x).prod() - 1)
    
    annual_df = pd.DataFrame({
        'Year': annual_strategy.index.year,
        'Strategy_Return': annual_strategy.values * 100,
        'Market_Return': annual_market.values * 100,
        'Outperformance': (annual_strategy.values - annual_market.values) * 100
    })
    
    return annual_df


def calculate_rolling_sharpe(df, window=30, risk_free_rate=0.06):
    """
    Calculate rolling Sharpe ratio.
    
    Args:
        df: DataFrame with Strategy_Return column
        window: Rolling window in days
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Series of rolling Sharpe ratios
    """
    returns = df['Strategy_Return']
    rolling_mean = returns.rolling(window).mean() * 252
    rolling_std = returns.rolling(window).std() * np.sqrt(252)
    
    rolling_sharpe = (rolling_mean - risk_free_rate) / rolling_std
    
    return rolling_sharpe
