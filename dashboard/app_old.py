"""
Professional NIFTY 50 Backtesting Dashboard

A clean, focused interface for quantitative strategy analysis.
Follows professional UI/UX principles with clear information hierarchy.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data_loader import fetch_data
from backtester import Backtester
from metrics import calculate_advanced_metrics, calculate_drawdown_recovery, calculate_trade_metrics, generate_insights
from analysis import (
    split_data, 
    compare_with_benchmark, 
    analyze_market_regimes,
    transaction_cost_sensitivity,
    multi_strategy_comparison
)
import datetime

# Page Config
st.set_page_config(
    page_title="NIFTY 50 Backtester Pro", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Custom CSS for premium look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: 600;
    }
    .info-box {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">📈 NIFTY 50 Backtesting Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Professional quantitative analysis with rigorous risk metrics</div>', unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.header("⚙️ Configuration")

# Strategy Selector
strategy = st.sidebar.selectbox(
    "Strategy Type",
    ["Momentum (SMA)", "Mean Reversion (Bollinger)", "RSI Strategy"],
    help="Select the trading strategy to backtest"
)

# Date Range
st.sidebar.subheader("📅 Date Range")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2015-01-01"))
today = datetime.date.today()
end_date = st.sidebar.date_input("End Date", today)

# Transaction Cost
st.sidebar.subheader("💰 Costs")
cost_bps = st.sidebar.number_input(
    "Transaction Cost (bps per side)", 
    min_value=0.0, 
    value=10.0, 
    step=1.0,
    help="Cost per trade side. Full round trip = 2x this value. Default 10 bps = 0.1%"
)
tx_cost = cost_bps / 10000.0

# Strategy Parameters (conditional based on strategy)
st.sidebar.subheader("🎯 Strategy Parameters")

params = {}
if "Momentum" in strategy:
    params['sma_window'] = st.sidebar.slider(
        "SMA Window", 
        min_value=10, 
        max_value=200, 
        value=50,
        help="Simple Moving Average period"
    )
elif "Mean Reversion" in strategy:
    params['sma_window'] = st.sidebar.slider(
        "SMA Window", 
        min_value=10, 
        max_value=100, 
        value=20,
        help="SMA period for Bollinger Bands"
    )
    params['std_dev'] = st.sidebar.slider(
        "Band Width (Std Dev)", 
        min_value=1.0, 
        max_value=4.0, 
        value=2.0, 
        step=0.1,
        help="Number of standard deviations for bands"
    )
else:  # RSI Strategy
    params['rsi_period'] = st.sidebar.slider(
        "RSI Period", 
        min_value=5, 
        max_value=30, 
        value=14,
        help="Period for RSI calculation"
    )
    params['oversold'] = st.sidebar.slider(
        "Oversold Level", 
        min_value=10, 
        max_value=40, 
        value=30,
        help="RSI level to trigger buy signal"
    )
    params['overbought'] = st.sidebar.slider(
        "Overbought Level", 
        min_value=60, 
        max_value=90, 
        value=70,
        help="RSI level to trigger sell signal"
    )

# Risk Management
st.sidebar.subheader("🛡️ Risk Management")
position_size = st.sidebar.slider(
    "Position Size (% of capital)", 
    min_value=10, 
    max_value=100, 
    value=100,
    step=5,
    help="Percentage of capital to deploy per trade"
) / 100.0

use_risk_mgmt = st.sidebar.checkbox("Enable Stop-Loss / Take-Profit", value=False)
if use_risk_mgmt:
    stop_loss = st.sidebar.number_input(
        "Stop-Loss (%)", 
        min_value=-20.0, 
        max_value=-1.0, 
        value=-5.0,
        step=0.5,
        help="Exit trade if loss exceeds this percentage"
    ) / 100.0
    take_profit = st.sidebar.number_input(
        "Take-Profit (%)", 
        min_value=1.0, 
        max_value=50.0, 
        value=10.0,
        step=0.5,
        help="Exit trade if profit reaches this percentage"
    ) / 100.0
else:
    stop_loss = None
    take_profit = None

# Analysis Options
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Advanced Analysis")
show_regime = st.sidebar.checkbox("Market Regime Breakdown", value=False)
show_sensitivity = st.sidebar.checkbox("Cost Sensitivity Analysis", value=False)
show_comparison = st.sidebar.checkbox("Multi-Strategy Comparison", value=False)

# --- Data Loading with Error Handling ---
try:
    with st.spinner("📡 Loading NIFTY 50 data..."):
        df = fetch_data(start_date=str(start_date), end_date=str(end_date))
    
    if len(df) < 50:
        st.error("⚠️ Insufficient data for selected date range. Please extend the period.")
        st.stop()
        
except Exception as e:
    st.error(f"❌ Data loading error: {e}")
    st.error("Please check your internet connection or try a different date range.")
    st.stop()

# --- Backtest Execution ---
try:
    bt = Backtester(df, transaction_cost=tx_cost, stop_loss=stop_loss, take_profit=take_profit, position_size=position_size)
    
    if "Momentum" in strategy:
        # Check if SMA window is too large
        if params['sma_window'] > len(df) * 0.5:
            st.warning(f"⚠️ SMA window ({params['sma_window']}) is very large relative to data ({len(df)} days). Results may be unreliable.")
        res_df = bt.run_momentum(sma_window=params['sma_window'])
    elif "Mean Reversion" in strategy:
        if params['sma_window'] > len(df) * 0.5:
            st.warning(f"⚠️ SMA window ({params['sma_window']}) is very large relative to data ({len(df)} days). Results may be unreliable.")
        res_df = bt.run_mean_reversion(sma_window=params['sma_window'], std_dev=params['std_dev'])
    else:  # RSI Strategy
        res_df = bt.run_rsi(rsi_period=params['rsi_period'], oversold=params['oversold'], overbought=params['overbought'])
    
    # Save trade log
    bt.save_trade_log('d:/Trading_Project/data/trades.csv')
    
    # Calculate metrics
    metrics = calculate_advanced_metrics(res_df)
    trade_metrics = calculate_trade_metrics(bt.trades)
    dd_recovery = calculate_drawdown_recovery(res_df)
    benchmark_metrics = compare_with_benchmark(res_df)
    
except Exception as e:
    st.error(f"❌ Backtest execution error: {e}")
    st.error("This may be due to invalid parameters or data issues.")
    st.stop()

# --- TABS LAYOUT ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Performance", 
    "⚠️ Risk", 
    "💼 Trades",
    "🔬 Advanced"
])

# ==================== TAB 1: OVERVIEW ====================
with tab1:
    st.subheader("Key Performance Indicators")
    
    # Top 5 metrics - prominently displayed
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("CAGR", f"{metrics['CAGR']:.2%}")
    col2.metric("Sharpe Ratio", f"{metrics['Sharpe']:.2f}")
    col3.metric("Max Drawdown", f"{metrics['Max_Drawdown']:.2%}")
    col4.metric("Total Return", f"{metrics['Total_Return']:.2%}")
    col5.metric("Total Trades", f"{trade_metrics['Total_Trades']}")
    
    # Full metrics in expander (reduces cognitive load)
    with st.expander("📋 Show Full Metrics"):
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sortino Ratio", f"{metrics['Sortino']:.2f}")
    
    with col1:
        st.markdown("### 🎯 Strategy Performance")
        st.metric("CAGR", f"{metrics['CAGR']:.2%}")
        st.metric("Sharpe Ratio", f"{metrics['Sharpe']:.2f}")
        st.metric("Max Drawdown", f"{metrics['Max_Drawdown']:.2%}")
        st.metric("Volatility", f"{metrics['Volatility']:.2%}")
    
    with col2:
        st.markdown("### 📈 Buy & Hold Benchmark")
        st.metric("CAGR", f"{benchmark_metrics['CAGR']:.2%}")
        st.metric("Sharpe Ratio", f"{benchmark_metrics['Sharpe']:.2f}")
        st.metric("Max Drawdown", f"{benchmark_metrics['Max_Drawdown']:.2%}")
        st.metric("Volatility", f"{benchmark_metrics['Volatility']:.2%}")
    
    # Comparison bar chart
    st.markdown("### Comparative Metrics")
    
    comparison_df = pd.DataFrame({
        'Metric': ['CAGR', 'Sharpe', 'Max DD (abs)'],
        'Strategy': [
            metrics['CAGR'] * 100,
            metrics['Sharpe'],
            abs(metrics['Max_Drawdown']) * 100
        ],
        'Buy & Hold': [
            benchmark_metrics['CAGR'] * 100,
            benchmark_metrics['Sharpe'],
            abs(benchmark_metrics['Max_Drawdown']) * 100
        ]
    })
    
    fig_compare = go.Figure()
    fig_compare.add_trace(go.Bar(
        name='Strategy',
        x=comparison_df['Metric'],
        y=comparison_df['Strategy'],
        marker_color='#667eea'
    ))
    fig_compare.add_trace(go.Bar(
        name='Buy & Hold',
        x=comparison_df['Metric'],
        y=comparison_df['Buy & Hold'],
        marker_color='#9ca3af'
    ))
    fig_compare.update_layout(
        barmode='group',
        height=350,
        template='plotly_white',
        yaxis_title='Value'
    )
    st.plotly_chart(fig_compare, use_container_width=True)

# ==================== TAB 2: PERFORMANCE ====================
with tab2:
    st.subheader("Equity Curve")
    
    fig_equity = go.Figure()
    fig_equity.add_trace(go.Scatter(
        x=res_df.index, 
        y=res_df['Market_Equity'], 
        mode='lines', 
        name='Buy & Hold',
        line=dict(color='#9ca3af', width=2)
    ))
    fig_equity.add_trace(go.Scatter(
        x=res_df.index, 
        y=res_df['Strategy_Equity'], 
        mode='lines', 
        name=strategy,
        line=dict(color='#667eea', width=3)
    ))
    fig_equity.update_layout(
        xaxis_title="Date", 
        yaxis_title="Portfolio Value (₹)", 
        hovermode="x unified",
        height=500,
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    st.plotly_chart(fig_equity, use_container_width=True)
    
    # Daily Returns Distribution
    st.subheader("Return Distribution")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        returns = res_df['Strategy_Return'].dropna() * 100
        
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=returns,
            nbinsx=50,
            name='Daily Returns',
            marker_color='#667eea',
            opacity=0.7
        ))
        fig_hist.update_layout(
            xaxis_title="Daily Return (%)",
            yaxis_title="Frequency",
            height=400,
            template="plotly_white",
            showlegend=False
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("### Distribution Stats")
        st.metric("Mean", f"{returns.mean():.3f}%")
        st.metric("Std Dev", f"{returns.std():.3f}%")
        st.metric("Skewness", f"{metrics['Skewness']:.3f}")
        st.metric("Kurtosis", f"{metrics['Kurtosis']:.3f}")
        
        # Interpretation
        if metrics['Skewness'] > 0:
            st.info("✓ Positive skew: More upside potential")
        else:
            st.warning("⚠ Negative skew: Fat left tail")

# ==================== TAB 3: RISK ====================
with tab3:
    st.subheader("Drawdown Analysis")
    st.markdown("*Underwater plot showing peak-to-trough declines*")
    
    # Calculate drawdown series
    strat_ret = res_df['Strategy_Return'].fillna(0)
    cum_ret = (1 + strat_ret).cumprod()
    peak = cum_ret.cummax()
    drawdown_series = (cum_ret - peak) / peak * 100
    
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=res_df.index, 
        y=drawdown_series, 
        mode='lines', 
        name='Drawdown',
        fill='tozeroy',
        line=dict(color='#ef4444', width=2),
        fillcolor='rgba(239, 68, 68, 0.3)'
    ))
    fig_dd.update_layout(
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode="x unified",
        height=400,
        template="plotly_white",
        showlegend=False
    )
    st.plotly_chart(fig_dd, use_container_width=True)
    
    # Drawdown Recovery Metrics
    st.markdown("### Recovery Analysis")
    st.markdown("*How long did it take to recover from the worst drawdown?*")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Peak Date", dd_recovery['Peak_Date'].strftime('%Y-%m-%d') if dd_recovery['Peak_Date'] else "N/A")
    col2.metric("Trough Date", dd_recovery['Trough_Date'].strftime('%Y-%m-%d') if dd_recovery['Trough_Date'] else "N/A")
    
    if dd_recovery['Recovery_Date']:
        col3.metric("Recovery Date", dd_recovery['Recovery_Date'].strftime('%Y-%m-%d'))
        col4.metric("Recovery Duration", f"{dd_recovery['Recovery_Days']} days")
    else:
        col3.metric("Recovery Date", "Not Yet Recovered")
        col4.metric("Recovery Duration", "N/A")
    
    # Rolling Volatility (optional, in expander)
    with st.expander("📊 Show Rolling Volatility"):
        st.markdown("### Rolling 30-Day Volatility")
        
        rolling_vol = res_df['Strategy_Return'].rolling(30).std() * np.sqrt(252) * 100
        
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=res_df.index,
            y=rolling_vol,
            mode='lines',
            name='30-Day Volatility',
            line=dict(color='#f59e0b', width=2)
        ))
        fig_vol.update_layout(
            xaxis_title="Date",
            yaxis_title="Annualized Volatility (%)",
            height=350,
            template="plotly_white",
            showlegend=False
        )
        st.plotly_chart(fig_vol, use_container_width=True)

# ==================== TAB 4: TRADES ====================
with tab4:
    st.subheader("📋 Trade Log")
    
    if len(bt.trades) > 0:
        # Trade Statistics Summary
        st.markdown("### Trade Statistics")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", f"{trade_metrics['Total_Trades']}")
        col2.metric("Win Rate", f"{trade_metrics['Win_Rate_Trade']:.1%}")
        col3.metric("Avg Duration", f"{trade_metrics['Avg_Trade_Duration']:.1f} days")
        col4.metric("Profit Factor", f"{trade_metrics['Profit_Factor']:.2f}")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Avg Win", f"₹{trade_metrics['Avg_Win']:.2f}")
        col2.metric("Avg Loss", f"₹{trade_metrics['Avg_Loss']:.2f}")
        
        winning_trades = bt.trades[bt.trades['PnL'] > 0]
        losing_trades = bt.trades[bt.trades['PnL'] < 0]
        col3.metric("Winning Trades", f"{len(winning_trades)}")
        col4.metric("Losing Trades", f"{len(losing_trades)}")
        
        st.markdown("---")
        
        # Filters
        st.markdown("### Filter Trades")
        col1, col2 = st.columns(2)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by",
                ["All Trades", "Winning Trades Only", "Losing Trades Only"]
            )
        
        with col2:
            # Extract year from trades
            bt.trades['Year'] = pd.to_datetime(bt.trades['Entry_Date']).dt.year
            years = sorted(bt.trades['Year'].unique())
            selected_year = st.selectbox("Year", ["All"] + [str(y) for y in years])
        
        # Apply filters
        filtered_trades = bt.trades.copy()
        
        if filter_type == "Winning Trades Only":
            filtered_trades = filtered_trades[filtered_trades['PnL'] > 0]
        elif filter_type == "Losing Trades Only":
            filtered_trades = filtered_trades[filtered_trades['PnL'] < 0]
        
        if selected_year != "All":
            filtered_trades = filtered_trades[filtered_trades['Year'] == int(selected_year)]
        
        # Display filtered trades
        st.markdown(f"### Showing {len(filtered_trades)} trades")
        
        display_trades = filtered_trades.copy()
        display_trades['Entry_Date'] = pd.to_datetime(display_trades['Entry_Date']).dt.strftime('%Y-%m-%d')
        display_trades['Exit_Date'] = pd.to_datetime(display_trades['Exit_Date']).dt.strftime('%Y-%m-%d')
        display_trades['Duration'] = (
            pd.to_datetime(filtered_trades['Exit_Date']) - 
            pd.to_datetime(filtered_trades['Entry_Date'])
        ).dt.days
        
        # Drop the Year column for display
        display_trades = display_trades.drop(columns=['Year'])
        
        st.dataframe(
            display_trades.style.format({
                'Entry_Price': '{:.2f}',
                'Exit_Price': '{:.2f}',
                'PnL': '{:.2f}',
                'Return_Pct': '{:.2%}'
            }),
            use_container_width=True,
            height=400
        )
        
    else:
        st.warning("⚠️ No trades executed with current parameters.")
        st.info("Try adjusting the strategy parameters or date range.")

# ==================== TAB 5: ADVANCED ====================
with tab5:
    # Market Regime Analysis
    if show_regime:
        st.subheader("🌍 Market Regime Performance")
        st.markdown("*Performance breakdown by deterministic market regimes*")
        
        regime_df = analyze_market_regimes(res_df)
        
        if len(regime_df) > 0:
            st.dataframe(
                regime_df.style.format({
                    'Total_Return': '{:.2%}',
                    'Avg_Daily_Return': '{:.4f}',
                    'Volatility': '{:.2%}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No regime data available for selected date range.")
    
    # Transaction Cost Sensitivity
    if show_sensitivity:
        st.subheader("💰 Transaction Cost Sensitivity")
        st.markdown("*How do different cost assumptions affect performance?*")
        
        with st.spinner("Running sensitivity analysis..."):
            sensitivity_df = transaction_cost_sensitivity(
                df, 
                None, 
                params,
                costs=[0.0005, 0.001, 0.002, 0.003]  # 5, 10, 20, 30 bps
            )
        
        st.dataframe(
            sensitivity_df.style.format({
                'Transaction_Cost_bps': '{:.1f}',
                'CAGR': '{:.2%}',
                'Sharpe': '{:.2f}',
                'Max_Drawdown': '{:.2%}'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Visualization
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Scatter(
            x=sensitivity_df['Transaction_Cost_bps'],
            y=sensitivity_df['CAGR'] * 100,
            mode='lines+markers',
            name='CAGR',
            line=dict(color='#667eea', width=3)
        ))
        fig_sens.update_layout(
            xaxis_title="Transaction Cost (bps)",
            yaxis_title="CAGR (%)",
            height=350,
            template="plotly_white"
        )
        st.plotly_chart(fig_sens, use_container_width=True)
    
    # Multi-Strategy Comparison
    if show_comparison:
        st.subheader("🔬 Multi-Strategy Comparison")
        st.markdown("*Compare different strategy configurations*")
        
        with st.spinner("Comparing strategies..."):
            comparison_df = multi_strategy_comparison(df)
        
        st.dataframe(
            comparison_df.style.format({
                'CAGR': '{:.2%}',
                'Sharpe': '{:.2f}',
                'Sortino': '{:.2f}',
                'Calmar': '{:.2f}',
                'Max_Drawdown': '{:.2%}',
                'Win_Rate': '{:.1%}'
            }),
            use_container_width=True,
            hide_index=True
        )

# --- ASSUMPTIONS & LIMITATIONS ---
st.markdown("---")
with st.expander("ℹ️ Execution Model & Assumptions"):
    st.markdown("""
    ### Execution Model
    - **Signal Generation**: Signals are generated at market close based on closing prices
    - **Trade Execution**: All trades execute at the **next day's open** price
    - **Return Calculation**: Both strategy and benchmark use **open-to-open** returns for consistency
    - **Look-Ahead Bias**: Eliminated via signal shifting (Position = Signal.shift(1))
    
    ### Transaction Costs
    - **Default**: 10 bps (0.1%) per side
    - **Full Round Trip**: 20 bps (entry + exit)
    - **Application**: Costs applied only on actual position changes
    
    ### Assumptions
    - **Dividends**: Modeled as a constant 1.5% annual yield added to benchmark returns (simplified)
    - **No Taxes**: Tax implications not modeled
    - **No Slippage**: Assumes execution at exact open price (beyond transaction costs)
    - **No Liquidity Constraints**: Assumes infinite liquidity
    - **No Margin/Leverage**: Assumes cash-only trading
    - **Single Asset**: NIFTY 50 index only
    - **SL/TP Timing**: Stop-loss and take-profit checked at end-of-day close, exit at next day's open
    
    ### Data Source
    - **Provider**: Yahoo Finance (via yfinance)
    - **Frequency**: Daily OHLC data
    - **Adjustments**: Prices are adjusted for splits/bonuses
    
    ### Important Notes
    - Past performance does not guarantee future results
    - This is a simplified backtest for educational purposes
    - Real-world trading involves additional complexities
    """)

# --- EXPORT SECTION ---
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Export Results")

if st.sidebar.button("💾 Export All Data"):
    try:
        # Save results
        res_df.to_csv("d:/Trading_Project/data/strategy_results.csv")
        
        # Save summary metrics
        summary = {
            **metrics,
            **trade_metrics,
            "Strategy": strategy,
            "Parameters": str(params),
            "Transaction_Cost_bps": cost_bps
        }
        pd.DataFrame([summary]).to_csv("d:/Trading_Project/data/summary_metrics.csv", index=False)
        
        st.sidebar.success("✅ Exported to data/ folder!")
    except Exception as e:
        st.sidebar.error(f"Export failed: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.875rem;'>
    <p><strong>Return Basis:</strong> Open-to-Open for both Strategy and Benchmark | 
    <strong>Execution:</strong> Next Day Open | 
    <strong>Look-Ahead Bias:</strong> Eliminated</p>
</div>
""", unsafe_allow_html=True)
