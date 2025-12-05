"""
Professional NIFTY 50 Backtesting Dashboard
Bloomberg Terminal-Inspired Dark Theme
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sys
import os
import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from data_loader import fetch_data
from backtester import Backtester
from metrics import (calculate_advanced_metrics, calculate_drawdown_recovery, 
                     calculate_trade_metrics, generate_insights)
from analysis import (
    compare_with_benchmark, analyze_market_regimes,
    transaction_cost_sensitivity, multi_strategy_comparison,
    calculate_monthly_returns, calculate_annual_returns, calculate_rolling_sharpe
)
from styles import COLORS, CUSTOM_CSS, get_alert_class, get_alert_message, format_metric_delta

# Page Config
st.set_page_config(
    page_title="NIFTY 50 Backtester", 
    layout="wide", 
    page_icon="📈",
    initial_sidebar_state="expanded"
)

# Apply Custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==================== SIDEBAR ====================
st.sidebar.header("⚙️ Configuration")

# Strategy
strategy = st.sidebar.selectbox(
    "Strategy",
    ["Momentum (SMA)", "Mean Reversion (Bollinger)", "RSI Strategy"]
)

# Date Range
st.sidebar.subheader("📅 Date Range")
start_date = st.sidebar.date_input("Start", pd.to_datetime("2015-01-01"))
end_date = st.sidebar.date_input("End", datetime.date.today())

# Transaction Cost
st.sidebar.subheader("💰 Costs")
cost_bps = st.sidebar.number_input("Transaction Cost (bps)", 0.0, 50.0, 10.0, 1.0)
tx_cost = cost_bps / 10000.0

# Strategy Parameters
st.sidebar.subheader("🎯 Parameters")
params = {}
if "Momentum" in strategy:
    params['sma_window'] = st.sidebar.slider("SMA Window", 10, 200, 50)
elif "Mean Reversion" in strategy:
    params['sma_window'] = st.sidebar.slider("SMA Window", 10, 100, 20)
    params['std_dev'] = st.sidebar.slider("Std Dev", 1.0, 4.0, 2.0, 0.1)
else:  # RSI
    params['rsi_period'] = st.sidebar.slider("RSI Period", 5, 30, 14)
    params['oversold'] = st.sidebar.slider("Oversold", 10, 40, 30)
    params['overbought'] = st.sidebar.slider("Overbought", 60, 90, 70)

# Risk Management
st.sidebar.subheader("🛡️ Risk Management")
position_size = st.sidebar.slider("Position Size (%)", 10, 100, 100, 5) / 100.0
use_risk_mgmt = st.sidebar.checkbox("Enable SL/TP")
if use_risk_mgmt:
    stop_loss = st.sidebar.number_input("Stop-Loss (%)", -20.0, -1.0, -5.0, 0.5) / 100.0
    take_profit = st.sidebar.number_input("Take-Profit (%)", 1.0, 50.0, 10.0, 0.5) / 100.0
else:
    stop_loss = None
    take_profit = None

# ==================== DATA LOADING ====================
try:
    with st.spinner("Loading data..."):
        df = fetch_data(start_date=str(start_date), end_date=str(end_date))
    if len(df) < 50:
        st.error("Insufficient data")
        st.stop()
except Exception as e:
    st.error(f"Data error: {e}")
    st.stop()

# ==================== BACKTEST ====================
try:
    bt = Backtester(df, transaction_cost=tx_cost, stop_loss=stop_loss, 
                    take_profit=take_profit, position_size=position_size)
    
    if "Momentum" in strategy:
        res_df = bt.run_momentum(sma_window=params['sma_window'])
    elif "Mean Reversion" in strategy:
        res_df = bt.run_mean_reversion(sma_window=params['sma_window'], std_dev=params['std_dev'])
    else:
        res_df = bt.run_rsi(rsi_period=params['rsi_period'], 
                           oversold=params['oversold'], overbought=params['overbought'])
    
    metrics = calculate_advanced_metrics(res_df)
    trade_metrics = calculate_trade_metrics(bt.trades)
    dd_recovery = calculate_drawdown_recovery(res_df)
    benchmark_metrics = compare_with_benchmark(res_df)
    insights = generate_insights(res_df, metrics, bt.trades, strategy)
    
except Exception as e:
    st.error(f"Backtest error: {e}")
    st.stop()

# ==================== HELPER FUNCTIONS ====================
def create_metric_card(label, value, delta=None, format_pct=True):
    """Create a metric card with optional delta."""
    if delta:
        arrow, css_class, diff_val = delta
        delta_html = f'<div class="metric-delta {css_class}">{arrow} {diff_val:.2f}{"%" if format_pct else ""} vs benchmark</div>'
    else:
        delta_html = ""
    
    value_str = f"{value:.2f}%" if format_pct else f"{value:.2f}"
    
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value_str}</div>
        {delta_html}
    </div>
    """

# ==================== MAIN DASHBOARD ====================

# Title
st.markdown('<h1>📈 NIFTY 50 Backtesting Results</h1>', unsafe_allow_html=True)

# Alert Banner
alert_class = get_alert_class(metrics['CAGR'], metrics['Sharpe'])
alert_msg = get_alert_message(metrics['CAGR'], metrics['Sharpe'])
st.markdown(f'<div class="alert-banner {alert_class}">{alert_msg}</div>', unsafe_allow_html=True)

# ==================== TABS ====================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Summary", 
    "📈 Performance", 
    "⚠️ Risk", 
    "💼 Trades",
    "🔬 Advanced"
])

# ==================== TAB 1: SUMMARY ====================
with tab1:
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        delta = format_metric_delta(metrics['CAGR'] * 100, benchmark_metrics['CAGR'] * 100, True)
        st.markdown(create_metric_card("CAGR", metrics['CAGR'] * 100, delta, False), unsafe_allow_html=True)
    
    with col2:
        delta = format_metric_delta(metrics['Sharpe'], benchmark_metrics['Sharpe'], True)
        st.markdown(create_metric_card("Sharpe Ratio", metrics['Sharpe'], delta, False), unsafe_allow_html=True)
    
    with col3:
        delta = format_metric_delta(metrics['Max_Drawdown'] * 100, benchmark_metrics['Max_Drawdown'] * 100, False)
        st.markdown(create_metric_card("Max Drawdown", metrics['Max_Drawdown'] * 100, delta, False), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card("Total Trades", trade_metrics['Total_Trades'], None, False), unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Equity Curve
    st.markdown("### Equity Curve")
    
    fig = go.Figure()
    
    # Benchmark
    fig.add_trace(go.Scatter(
        x=res_df.index,
        y=res_df['Market_Equity'],
        mode='lines',
        name='Buy & Hold',
        line=dict(color=COLORS['text_secondary'], width=2, dash='dot')
    ))
    
    # Strategy
    fig.add_trace(go.Scatter(
        x=res_df.index,
        y=res_df['Strategy_Equity'],
        mode='lines',
        name=strategy,
        line=dict(color=COLORS['accent'], width=3)
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_primary'],
        font=dict(color=COLORS['text_primary']),
        height=500,
        hovermode="x unified",
        legend=dict(bgcolor=COLORS['bg_card'], bordercolor=COLORS['text_muted'])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Insights
    st.markdown("### Key Insights")
    insights_html = '<div class="insight-list"><ul>'
    for insight in insights[:5]:  # Limit to 5
        insights_html += f'<li>{insight}</li>'
    insights_html += '</ul></div>'
    st.markdown(insights_html, unsafe_allow_html=True)

# ==================== TAB 2: PERFORMANCE ====================
with tab2:
    st.markdown("### Performance Analysis")
    
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.markdown("#### Monthly Returns Heatmap")
        try:
            monthly_returns = calculate_monthly_returns(res_df)
            
            fig = go.Figure(data=go.Heatmap(
                z=monthly_returns.values,
                x=monthly_returns.columns,
                y=monthly_returns.index,
                colorscale='RdYlGn',
                zmid=0,
                text=np.round(monthly_returns.values, 1),
                texttemplate='%{text}',
                textfont={"size": 10, "color": "#0E1117"}
            ))
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['bg_card'],
                font=dict(color=COLORS['text_primary']),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Heatmap unavailable")
    
    with col2:
        st.markdown("#### Rolling Sharpe (30d)")
        try:
            rolling_sharpe = calculate_rolling_sharpe(res_df, window=30)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=res_df.index,
                y=rolling_sharpe,
                mode='lines',
                line=dict(color=COLORS['accent'], width=2),
                fill='tozeroy',
                fillcolor=f'rgba(0, 212, 255, 0.1)'
            ))
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['bg_primary'],
                font=dict(color=COLORS['text_primary']),
                height=400,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.info("Rolling Sharpe unavailable")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Annual Returns
    st.markdown("#### Annual Returns")
    try:
        annual_returns = calculate_annual_returns(res_df)
        st.dataframe(annual_returns, use_container_width=True, hide_index=True)
    except:
        st.info("Annual returns unavailable")

# ==================== TAB 3: RISK ====================
with tab3:
    st.markdown("### Risk Analysis")
    
    # Drawdown Chart
    strat_ret = res_df['Strategy_Return'].fillna(0)
    cum_ret = (1 + strat_ret).cumprod()
    peak = cum_ret.cummax()
    drawdown_series = (cum_ret - peak) / peak * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=res_df.index,
        y=drawdown_series,
        mode='lines',
        fill='tozeroy',
        line=dict(color=COLORS['danger'], width=2),
        fillcolor=f'rgba(255, 82, 82, 0.2)'
    ))
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS['bg_primary'],
        plot_bgcolor=COLORS['bg_primary'],
        font=dict(color=COLORS['text_primary']),
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Risk Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Max Drawdown", f"{metrics['Max_Drawdown']:.2%}")
    col2.metric("Calmar Ratio", f"{metrics['Calmar']:.2f}")
    col3.metric("Sortino Ratio", f"{metrics['Sortino']:.2f}")
    col4.metric("Volatility", f"{metrics['Volatility']:.2%}")

# ==================== TAB 4: TRADES ====================
with tab4:
    st.markdown("### Trade Analysis")
    
    if len(bt.trades) > 0:
        # Trade Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Trades", trade_metrics['Total_Trades'])
        col2.metric("Win Rate", f"{trade_metrics['Win_Rate_Trade']:.1%}")
        col3.metric("Profit Factor", f"{trade_metrics['Profit_Factor']:.2f}")
        col4.metric("Avg Duration", f"{trade_metrics['Avg_Trade_Duration']:.1f} days")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Trade Log
        st.markdown("#### Trade Log")
        display_trades = bt.trades.copy()
        st.dataframe(display_trades, use_container_width=True, height=400)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # Scatter Plot
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Returns per Trade")
            colors = [COLORS['chart_positive'] if r > 0 else COLORS['chart_negative'] 
                     for r in bt.trades['Return_Pct']]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=list(range(1, len(bt.trades) + 1)),
                y=bt.trades['Return_Pct'] * 100,
                mode='markers',
                marker=dict(size=10, color=colors)
            ))
            
            fig.add_hline(y=0, line_dash="dash", line_color=COLORS['text_muted'])
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['bg_primary'],
                font=dict(color=COLORS['text_primary']),
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Holding Periods")
            holding_periods = (
                pd.to_datetime(bt.trades['Exit_Date']) - 
                pd.to_datetime(bt.trades['Entry_Date'])
            ).dt.days
            
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=holding_periods,
                nbinsx=20,
                marker_color=COLORS['accent']
            ))
            
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor=COLORS['bg_primary'],
                plot_bgcolor=COLORS['bg_primary'],
                font=dict(color=COLORS['text_primary']),
                height=350,
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No trades executed")

# ==================== TAB 5: ADVANCED ====================
with tab5:
    st.markdown("### Advanced Analysis")
    
    # Market Regimes
    try:
        regime_df = analyze_market_regimes(res_df)
        if len(regime_df) > 0:
            st.markdown("#### Market Regime Performance")
            st.dataframe(regime_df, use_container_width=True, hide_index=True)
    except:
        st.info("Regime analysis unavailable")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # Cost Sensitivity
    try:
        with st.spinner("Running sensitivity analysis..."):
            sensitivity_df = transaction_cost_sensitivity(df, None, params, costs=[0.0005, 0.001, 0.002])
        st.markdown("#### Transaction Cost Sensitivity")
        st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
    except:
        st.info("Sensitivity analysis unavailable")
