"""
Unit tests for backtester metrics and core functionality.

These tests ensure mathematical correctness and handle edge cases.
"""

import pandas as pd
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from metrics import calculate_advanced_metrics, calculate_trade_metrics, calculate_drawdown_recovery
from backtester import Backtester


def test_max_drawdown_synthetic():
    """Test max drawdown calculation on a known synthetic equity curve."""
    # Create a simple equity curve: 100 -> 150 -> 100 -> 200
    dates = pd.date_range('2020-01-01', periods=4, freq='D')
    equity = [100, 150, 100, 200]
    
    df = pd.DataFrame({
        'Strategy_Return': [0, 0.5, -0.333333, 1.0],
        'Strategy_Equity': equity,
        'Position': [1, 1, 1, 1]
    }, index=dates)
    
    metrics = calculate_advanced_metrics(df)
    
    # Max drawdown should be (100-150)/150 = -33.33%
    expected_dd = -0.333333
    assert abs(metrics['Max_Drawdown'] - expected_dd) < 0.01, \
        f"Expected drawdown ~{expected_dd}, got {metrics['Max_Drawdown']}"
    
    print("✓ test_max_drawdown_synthetic passed")


def test_sharpe_constant_returns():
    """Test Sharpe ratio on constant positive returns (should be very high)."""
    # Constant 1% daily return
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    daily_return = 0.01
    
    returns = np.full(252, daily_return)
    equity = 100 * (1 + pd.Series(returns)).cumprod()
    
    df = pd.DataFrame({
        'Strategy_Return': returns,
        'Strategy_Equity': equity,
        'Position': np.ones(252)
    }, index=dates)
    
    metrics = calculate_advanced_metrics(df, risk_free_rate=0.06)
    
    # With zero volatility, Sharpe should be very high or infinite
    # Since we have constant returns, std should be 0
    assert metrics['Sharpe'] == 0 or metrics['Sharpe'] > 100, \
        f"Expected very high Sharpe for constant returns, got {metrics['Sharpe']}"
    
    print("✓ test_sharpe_constant_returns passed")


def test_sortino_no_negative_returns():
    """Test Sortino ratio when there are no negative returns."""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    
    # All positive returns
    returns = np.random.uniform(0.001, 0.02, 100)
    equity = 100 * (1 + pd.Series(returns)).cumprod()
    
    df = pd.DataFrame({
        'Strategy_Return': returns,
        'Strategy_Equity': equity,
        'Position': np.ones(100)
    }, index=dates)
    
    metrics = calculate_advanced_metrics(df)
    
    # Sortino should be 0 or very large when no downside
    assert metrics['Sortino'] >= 0, \
        f"Sortino should be non-negative, got {metrics['Sortino']}"
    
    print("✓ test_sortino_no_negative_returns passed")


def test_calmar_zero_drawdown():
    """Test Calmar ratio when max drawdown is zero (only gains)."""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    
    # Monotonically increasing equity (no drawdown)
    returns = np.random.uniform(0.001, 0.01, 100)
    equity = 100 * (1 + pd.Series(returns)).cumprod()
    
    df = pd.DataFrame({
        'Strategy_Return': returns,
        'Strategy_Equity': equity,
        'Position': np.ones(100)
    }, index=dates)
    
    metrics = calculate_advanced_metrics(df)
    
    # Calmar should be 0 or very large when no drawdown
    assert metrics['Calmar'] >= 0, \
        f"Calmar should be non-negative, got {metrics['Calmar']}"
    
    print("✓ test_calmar_zero_drawdown passed")


def test_empty_trades():
    """Test that empty trade DataFrame returns sensible defaults."""
    empty_trades = pd.DataFrame(columns=['Entry_Date', 'Exit_Date', 'PnL', 'Return_Pct'])
    
    trade_metrics = calculate_trade_metrics(empty_trades)
    
    assert trade_metrics['Total_Trades'] == 0
    assert trade_metrics['Win_Rate_Trade'] == 0
    assert trade_metrics['Profit_Factor'] == 0
    assert trade_metrics['Avg_Win'] == 0
    assert trade_metrics['Avg_Loss'] == 0
    
    print("✓ test_empty_trades passed")


def test_profit_factor_calculation():
    """Test profit factor calculation on known trades."""
    trades = pd.DataFrame({
        'Entry_Date': pd.date_range('2020-01-01', periods=5, freq='D'),
        'Exit_Date': pd.date_range('2020-01-02', periods=5, freq='D'),
        'PnL': [100, -50, 200, -30, 150],  # Total wins: 450, Total losses: 80
        'Return_Pct': [0.01, -0.005, 0.02, -0.003, 0.015]
    })
    
    trade_metrics = calculate_trade_metrics(trades)
    
    # Profit factor = 450 / 80 = 5.625
    expected_pf = 450 / 80
    assert abs(trade_metrics['Profit_Factor'] - expected_pf) < 0.01, \
        f"Expected profit factor {expected_pf}, got {trade_metrics['Profit_Factor']}"
    
    # Win rate = 3/5 = 60%
    assert abs(trade_metrics['Win_Rate_Trade'] - 0.6) < 0.01, \
        f"Expected win rate 0.6, got {trade_metrics['Win_Rate_Trade']}"
    
    print("✓ test_profit_factor_calculation passed")


def test_backtester_trivial_strategy():
    """Test backtester on trivial price series with known outcome."""
    # Create simple price data: always increasing
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    data = pd.DataFrame({
        'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
        'Close': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'High': [102, 103, 104, 105, 106, 107, 108, 109, 110, 111],
        'Low': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109]
    }, index=dates)
    
    bt = Backtester(data, initial_capital=10000, transaction_cost=0.0)
    
    # Run momentum with very short SMA (should always be in position after warmup)
    result = bt.run_momentum(sma_window=2)
    
    # Should have positive returns since price always increases
    final_equity = result['Strategy_Equity'].iloc[-1]
    assert final_equity >= 10000, \
        f"Expected positive returns on increasing prices, got final equity {final_equity}"
    
    print("✓ test_backtester_trivial_strategy passed")


def test_win_rate_definitions():
    """Test that win rate calculations are distinct for trades vs days."""
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    
    # 7 positive days, 3 negative days
    returns = [0.01, 0.02, -0.01, 0.01, -0.005, 0.015, 0.01, -0.01, 0.02, 0.01]
    equity = 100 * (1 + pd.Series(returns)).cumprod()
    
    df = pd.DataFrame({
        'Strategy_Return': returns,
        'Strategy_Equity': equity,
        'Position': np.ones(10)
    }, index=dates)
    
    metrics = calculate_advanced_metrics(df)
    
    # Win rate daily should be 7/10 = 70%
    expected_win_rate = 7 / 10
    assert abs(metrics['Win_Rate_Daily'] - expected_win_rate) < 0.01, \
        f"Expected daily win rate {expected_win_rate}, got {metrics['Win_Rate_Daily']}"
    
    print("✓ test_win_rate_definitions passed")


def run_all_tests():
    """Run all unit tests."""
    print("\n" + "="*60)
    print("Running Unit Tests for Trading Backtester")
    print("="*60 + "\n")
    
    tests = [
        test_max_drawdown_synthetic,
        test_sharpe_constant_returns,
        test_sortino_no_negative_returns,
        test_calmar_zero_drawdown,
        test_empty_trades,
        test_profit_factor_calculation,
        test_backtester_trivial_strategy,
        test_win_rate_definitions
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
