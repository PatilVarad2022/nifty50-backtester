"""
Professional-grade metrics calculation module.

All metrics are mathematically correct and handle edge cases gracefully.
"""

import pandas as pd
import numpy as np
from scipy import stats


def calculate_advanced_metrics(df: pd.DataFrame, risk_free_rate: float = 0.06) -> dict:
    """
    Calculate comprehensive risk and performance metrics.
    
    All metrics use open-to-open strategy returns for consistency.
    
    Args:
        df: DataFrame with 'Strategy_Return' and 'Strategy_Equity' columns
        risk_free_rate: Annual risk-free rate (default 6% for India)
    
    Returns:
        Dictionary of metrics with proper handling of edge cases
    """
    strat_ret = df['Strategy_Return'].dropna()
    
    if len(strat_ret) == 0:
        return _empty_metrics()
    
    # Basic metrics
    days = (df.index[-1] - df.index[0]).days
    if days == 0:
        return _empty_metrics()
        
    total_return = (df['Strategy_Equity'].iloc[-1] / df['Strategy_Equity'].iloc[0]) - 1
    cagr = (1 + total_return) ** (365.0 / days) - 1
    
    # Volatility (annualized)
    volatility = strat_ret.std() * np.sqrt(252)
    
    # Sharpe Ratio
    excess_return = strat_ret.mean() * 252 - risk_free_rate
    sharpe = excess_return / volatility if volatility != 0 else np.nan
    
    # Sortino Ratio (downside deviation only)
    downside_ret = strat_ret[strat_ret < 0]
    if len(downside_ret) > 0:
        downside_std = downside_ret.std() * np.sqrt(252)
        sortino = excess_return / downside_std if downside_std != 0 else np.nan
    else:
        # No negative returns - Sortino is very high or undefined
        sortino = np.inf if excess_return > 0 else np.nan
    
    # Drawdown metrics
    cum_ret = (1 + strat_ret).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    max_drawdown = drawdown.min()
    
    # Calmar Ratio
    if max_drawdown == 0:
        # No drawdown - Calmar is very high or undefined
        calmar = np.inf if cagr > 0 else np.nan
    else:
        calmar = cagr / abs(max_drawdown)
    
    # Stability (R² of log equity curve vs time)
    equity = df['Strategy_Equity'].values
    if len(equity) > 1 and np.all(equity > 0):
        log_equity = np.log(equity)
        x = np.arange(len(equity))
        try:
            slope, intercept, r_value, _, _ = stats.linregress(x, log_equity)
            stability = r_value ** 2
        except:
            stability = 0.0
    else:
        stability = 0.0
    
    # Distribution metrics
    skewness = strat_ret.skew()
    kurtosis = strat_ret.kurtosis()
    
    # Win rate (daily) - percentage of days with positive returns
    win_days = strat_ret[strat_ret > 0].count()
    total_days = strat_ret[strat_ret != 0].count()
    win_rate_daily = win_days / total_days if total_days > 0 else 0
    
    # Market exposure (percentage of time in position)
    position = df['Position'].dropna()
    exposure = (position > 0).sum() / len(position) if len(position) > 0 else 0
    
    return {
        "CAGR": cagr,
        "Total_Return": total_return,
        "Volatility": volatility,
        "Sharpe": sharpe if not np.isnan(sharpe) and not np.isinf(sharpe) else 0.0,
        "Sortino": sortino if not np.isnan(sortino) and not np.isinf(sortino) else 0.0,
        "Calmar": calmar if not np.isnan(calmar) and not np.isinf(calmar) else 0.0,
        "Max_Drawdown": max_drawdown,
        "Stability": stability,
        "Skewness": skewness if not np.isnan(skewness) else 0.0,
        "Kurtosis": kurtosis if not np.isnan(kurtosis) else 0.0,
        "Win_Rate_Daily": win_rate_daily,
        "Market_Exposure": exposure
    }


def calculate_drawdown_recovery(df: pd.DataFrame) -> dict:
    """
    Calculate drawdown recovery metrics.
    
    Returns:
        Dict with peak_date, trough_date, recovery_date, recovery_days, max_drawdown
    """
    strat_ret = df['Strategy_Return'].dropna()
    
    if len(strat_ret) == 0:
        return {
            "Peak_Date": None,
            "Trough_Date": None,
            "Recovery_Date": None,
            "Recovery_Days": None,
            "Max_Drawdown": 0.0
        }
    
    cum_ret = (1 + strat_ret).cumprod()
    peak = cum_ret.cummax()
    drawdown = (cum_ret - peak) / peak
    
    # Find max drawdown point
    trough_idx = drawdown.idxmin()
    trough_date = trough_idx
    
    # Find peak before trough
    peak_idx = cum_ret[:trough_idx].idxmax() if len(cum_ret[:trough_idx]) > 0 else cum_ret.index[0]
    peak_date = peak_idx
    
    # Find recovery (first time equity >= peak after trough)
    peak_value = cum_ret.loc[peak_idx]
    recovery_series = cum_ret[trough_idx:]
    recovery_points = recovery_series[recovery_series >= peak_value]
    
    if len(recovery_points) > 0:
        recovery_date = recovery_points.index[0]
        recovery_days = (recovery_date - peak_date).days
    else:
        recovery_date = None
        recovery_days = None
    
    return {
        "Peak_Date": peak_date,
        "Trough_Date": trough_date,
        "Recovery_Date": recovery_date,
        "Recovery_Days": recovery_days,
        "Max_Drawdown": drawdown.min()
    }


def calculate_trade_metrics(trades_df: pd.DataFrame) -> dict:
    """
    Calculate per-trade metrics from trade log.
    
    This is TRADE-LEVEL win rate and metrics, distinct from daily metrics.
    
    Args:
        trades_df: DataFrame with columns [Entry_Date, Exit_Date, PnL, Return_Pct]
    
    Returns:
        Dict with trade-level metrics
    """
    if len(trades_df) == 0:
        return {
            "Total_Trades": 0,
            "Win_Rate_Trade": 0.0,
            "Avg_Trade_Duration": 0.0,
            "Avg_Win": 0.0,
            "Avg_Loss": 0.0,
            "Profit_Factor": 0.0
        }
    
    winning_trades = trades_df[trades_df['PnL'] > 0]
    losing_trades = trades_df[trades_df['PnL'] < 0]
    
    # Win rate (per trade)
    win_rate = len(winning_trades) / len(trades_df) if len(trades_df) > 0 else 0
    
    # Average duration
    trades_df_copy = trades_df.copy()
    trades_df_copy['Duration'] = (
        pd.to_datetime(trades_df_copy['Exit_Date']) - 
        pd.to_datetime(trades_df_copy['Entry_Date'])
    ).dt.days
    avg_duration = trades_df_copy['Duration'].mean()
    
    # Win/Loss averages
    avg_win = winning_trades['PnL'].mean() if len(winning_trades) > 0 else 0
    avg_loss = losing_trades['PnL'].mean() if len(losing_trades) > 0 else 0
    
    # Profit factor: sum(wins) / abs(sum(losses))
    total_wins = winning_trades['PnL'].sum() if len(winning_trades) > 0 else 0
    total_losses = abs(losing_trades['PnL'].sum()) if len(losing_trades) > 0 else 0
    profit_factor = total_wins / total_losses if total_losses != 0 else (np.inf if total_wins > 0 else 0)
    
    # Cap profit factor at reasonable value for display
    if np.isinf(profit_factor):
        profit_factor = 999.99
    
    return {
        "Total_Trades": len(trades_df),
        "Win_Rate_Trade": win_rate,
        "Avg_Trade_Duration": avg_duration,
        "Avg_Win": avg_win,
        "Avg_Loss": avg_loss,
        "Profit_Factor": profit_factor
    }


def calculate_additional_risk_metrics(df: pd.DataFrame, confidence_level: float = 0.95) -> dict:
    """
    Calculate additional risk metrics: VaR, CVaR, Ulcer Index, Hit Rate.
    
    Args:
        df: DataFrame with Strategy_Return column
        confidence_level: Confidence level for VaR/CVaR (default 95%)
    
    Returns:
        Dict with additional risk metrics
    """
    strat_ret = df['Strategy_Return'].dropna()
    
    if len(strat_ret) == 0:
        return {
            "VaR_95": 0.0,
            "CVaR_95": 0.0,
            "Ulcer_Index": 0.0,
            "Hit_Rate": 0.0,
            "Best_Day": 0.0,
            "Worst_Day": 0.0
        }
    
    # Value at Risk (VaR) - Historical method
    var_95 = np.percentile(strat_ret, (1 - confidence_level) * 100)
    
    # Conditional VaR (CVaR) - Expected Shortfall
    # Average of returns worse than VaR
    cvar_95 = strat_ret[strat_ret <= var_95].mean() if len(strat_ret[strat_ret <= var_95]) > 0 else var_95
    
    # Ulcer Index - measures depth and duration of drawdowns
    equity = df['Strategy_Equity'].values
    if len(equity) > 1:
        running_max = pd.Series(equity).expanding().max()
        drawdown_pct = ((equity - running_max) / running_max) * 100  # As percentage
        ulcer_index = np.sqrt(np.mean(drawdown_pct ** 2))
    else:
        ulcer_index = 0.0
    
    # Hit Rate - percentage of positive return days
    hit_rate = (strat_ret > 0).sum() / len(strat_ret) if len(strat_ret) > 0 else 0
    
    # Best and worst days
    best_day = strat_ret.max()
    worst_day = strat_ret.min()
    
    return {
        "VaR_95": var_95,
        "CVaR_95": cvar_95,
        "Ulcer_Index": ulcer_index,
        "Hit_Rate": hit_rate,
        "Best_Day": best_day,
        "Worst_Day": worst_day
    }


def calculate_rolling_metrics(df: pd.DataFrame, window: int = 252) -> pd.DataFrame:
    """
    Calculate rolling performance metrics.
    
    Args:
        df: DataFrame with Strategy_Return column
        window: Rolling window in days (default 252 = 1 year)
    
    Returns:
        DataFrame with rolling metrics
    """
    strat_ret = df['Strategy_Return'].dropna()
    
    # Rolling Sharpe
    rolling_mean = strat_ret.rolling(window).mean() * 252
    rolling_std = strat_ret.rolling(window).std() * np.sqrt(252)
    rolling_sharpe = (rolling_mean - 0.06) / rolling_std
    
    # Rolling volatility
    rolling_vol = strat_ret.rolling(window).std() * np.sqrt(252)
    
    # Rolling max drawdown
    rolling_cumret = (1 + strat_ret).rolling(window).apply(lambda x: x.prod(), raw=False)
    rolling_peak = rolling_cumret.rolling(window).max()
    rolling_dd = (rolling_cumret - rolling_peak) / rolling_peak
    
    return pd.DataFrame({
        'Rolling_Sharpe': rolling_sharpe,
        'Rolling_Volatility': rolling_vol,
        'Rolling_Max_DD': rolling_dd
    }, index=df.index)


def _empty_metrics():
    """Return empty metrics dict for edge cases."""
    return {
        "CAGR": 0.0,
        "Total_Return": 0.0,
        "Volatility": 0.0,
        "Sharpe": 0.0,
        "Sortino": 0.0,
        "Calmar": 0.0,
        "Max_Drawdown": 0.0,
        "Stability": 0.0,
        "Skewness": 0.0,
        "Kurtosis": 0.0,
        "Win_Rate_Daily": 0.0,
        "Market_Exposure": 0.0
    }


def compare_strategy_benchmark(strategy_metrics: dict, benchmark_metrics: dict) -> pd.DataFrame:
    """
    Create side-by-side comparison of strategy vs benchmark metrics.
    
    Args:
        strategy_metrics: Dict of strategy metrics from calculate_advanced_metrics
        benchmark_metrics: Dict of benchmark metrics
        
    Returns:
        DataFrame with columns: Metric, Strategy, Benchmark, Difference
    """
    comparison_metrics = ['CAGR', 'Sharpe', 'Sortino', 'Calmar', 'Max_Drawdown', 'Volatility']
    
    data = []
    for metric in comparison_metrics:
        strat_val = strategy_metrics.get(metric, 0)
        bench_val = benchmark_metrics.get(metric, 0)
        diff = strat_val - bench_val
        
        data.append({
            'Metric': metric,
            'Strategy': strat_val,
            'Benchmark': bench_val,
            'Difference': diff
        })
    
    return pd.DataFrame(data)


def generate_insights(df: pd.DataFrame, metrics: dict, trades_df: pd.DataFrame, strategy_name: str) -> list:
    """
    Generate auto-generated insights about strategy performance.
    
    Args:
        df: Results DataFrame with returns and equity
        metrics: Metrics dictionary
        trades_df: Trade log DataFrame
        strategy_name: Name of the strategy
        
    Returns:
        List of insight strings
    """
    insights = []
    
    # Performance insights
    cagr = metrics['CAGR']
    if cagr > 0.15:
        insights.append(f"✅ Strong performance with {cagr:.1%} annual return")
    elif cagr > 0:
        insights.append(f"📊 Moderate performance with {cagr:.1%} annual return")
    else:
        insights.append(f"⚠️ Negative performance with {cagr:.1%} annual return")
    
    # Risk-adjusted returns
    sharpe = metrics['Sharpe']
    if sharpe > 1.5:
        insights.append(f"🎯 Excellent risk-adjusted returns (Sharpe: {sharpe:.2f})")
    elif sharpe > 1.0:
        insights.append(f"✅ Good risk-adjusted returns (Sharpe: {sharpe:.2f})")
    elif sharpe > 0:
        insights.append(f"📊 Positive but modest risk-adjusted returns (Sharpe: {sharpe:.2f})")
    else:
        insights.append(f"⚠️ Poor risk-adjusted returns (Sharpe: {sharpe:.2f})")
    
    # Drawdown analysis
    max_dd = abs(metrics['Max_Drawdown'])
    if max_dd < 0.10:
        insights.append(f"🛡️ Low drawdown risk ({max_dd:.1%} max drawdown)")
    elif max_dd < 0.20:
        insights.append(f"📊 Moderate drawdown risk ({max_dd:.1%} max drawdown)")
    else:
        insights.append(f"⚠️ High drawdown risk ({max_dd:.1%} max drawdown)")
    
    # Trade frequency
    if len(trades_df) > 0:
        days = (df.index[-1] - df.index[0]).days
        trades_per_year = len(trades_df) / (days / 365.25)
        
        if trades_per_year < 10:
            insights.append(f"📅 Low-frequency strategy ({len(trades_df)} trades, ~{trades_per_year:.0f}/year)")
        elif trades_per_year < 50:
            insights.append(f"📊 Medium-frequency strategy ({len(trades_df)} trades, ~{trades_per_year:.0f}/year)")
        else:
            insights.append(f"⚡ High-frequency strategy ({len(trades_df)} trades, ~{trades_per_year:.0f}/year)")
        
        # Win rate insight
        win_rate = trades_df[trades_df['PnL'] > 0].shape[0] / len(trades_df) if len(trades_df) > 0 else 0
        if win_rate > 0.5:
            insights.append(f"✅ High win rate ({win_rate:.1%} of trades profitable)")
        else:
            insights.append(f"📊 Win rate: {win_rate:.1%} (relies on larger wins)")
    
    # Market exposure
    exposure = metrics['Market_Exposure']
    if exposure > 0.7:
        insights.append(f"📈 High market exposure ({exposure:.1%} of time invested)")
    elif exposure > 0.3:
        insights.append(f"📊 Moderate market exposure ({exposure:.1%} of time invested)")
    else:
        insights.append(f"💰 Low market exposure ({exposure:.1%} of time invested)")
    
    # Stability
    stability = metrics['Stability']
    if stability > 0.9:
        insights.append(f"📈 Very consistent growth pattern (R²: {stability:.2f})")
    elif stability > 0.7:
        insights.append(f"✅ Consistent growth pattern (R²: {stability:.2f})")
    
    return insights
