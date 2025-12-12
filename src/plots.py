"""
Professional plotting module for backtesting visualizations.

Generates publication-quality charts for:
- Equity curves
- Drawdown analysis
- Return distributions
- Rolling metrics
- Performance heatmaps
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 10


def plot_equity_curve(df: pd.DataFrame, 
                      strategy_name: str = "Strategy",
                      save_path: Optional[str] = None,
                      show_benchmark: bool = True) -> None:
    """
    Plot equity curve with strategy vs benchmark.
    
    Args:
        df: DataFrame with Strategy_Equity and Market_Equity columns
        strategy_name: Name of the strategy for the title
        save_path: Path to save the figure (optional)
        show_benchmark: Whether to show benchmark comparison
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot strategy equity
    ax.plot(df.index, df['Strategy_Equity'], 
            label=f'{strategy_name}', 
            linewidth=2, 
            color='#2E86AB',
            alpha=0.9)
    
    # Plot benchmark if requested
    if show_benchmark and 'Market_Equity' in df.columns:
        ax.plot(df.index, df['Market_Equity'], 
                label='NIFTY 50 Buy & Hold', 
                linewidth=2, 
                color='#A23B72',
                alpha=0.7,
                linestyle='--')
    
    # Formatting
    ax.set_title(f'Equity Curve: {strategy_name} vs NIFTY 50', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value (₹)', fontsize=12)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Format y-axis as currency
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    # Add shaded regions for major market events (optional)
    # COVID crash
    if pd.Timestamp('2020-03-01') in df.index and pd.Timestamp('2020-06-30') in df.index:
        ax.axvspan(pd.Timestamp('2020-03-01'), pd.Timestamp('2020-06-30'), 
                   alpha=0.1, color='red', label='COVID Crash')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved equity curve to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_drawdown(df: pd.DataFrame, 
                  strategy_name: str = "Strategy",
                  save_path: Optional[str] = None) -> None:
    """
    Plot underwater (drawdown) chart.
    
    Args:
        df: DataFrame with Strategy_Equity column
        strategy_name: Name of the strategy
        save_path: Path to save the figure
    """
    # Calculate drawdown
    equity = df['Strategy_Equity']
    running_max = equity.expanding().max()
    drawdown = (equity - running_max) / running_max
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot drawdown
    ax.fill_between(df.index, drawdown * 100, 0, 
                     color='#C1121F', alpha=0.6, label='Drawdown')
    ax.plot(df.index, drawdown * 100, 
            color='#780000', linewidth=1.5, alpha=0.8)
    
    # Formatting
    ax.set_title(f'Drawdown Analysis: {strategy_name}', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Drawdown (%)', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
    
    # Add max drawdown annotation
    max_dd_idx = drawdown.idxmin()
    max_dd_val = drawdown.min() * 100
    ax.annotate(f'Max DD: {max_dd_val:.2f}%', 
                xy=(max_dd_idx, max_dd_val),
                xytext=(max_dd_idx, max_dd_val - 5),
                arrowprops=dict(arrowstyle='->', color='red', lw=2),
                fontsize=11, fontweight='bold', color='red')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved drawdown chart to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_returns_distribution(df: pd.DataFrame, 
                               strategy_name: str = "Strategy",
                               save_path: Optional[str] = None) -> None:
    """
    Plot return distribution with statistics.
    
    Args:
        df: DataFrame with Strategy_Return column
        strategy_name: Name of the strategy
        save_path: Path to save the figure
    """
    returns = df['Strategy_Return'].dropna() * 100  # Convert to percentage
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Histogram
    ax.hist(returns, bins=50, color='#2E86AB', alpha=0.7, edgecolor='black')
    
    # Add normal distribution overlay
    mu, sigma = returns.mean(), returns.std()
    x = np.linspace(returns.min(), returns.max(), 100)
    ax.plot(x, len(returns) * (returns.max() - returns.min()) / 50 * 
            (1/(sigma * np.sqrt(2*np.pi))) * np.exp(-0.5*((x-mu)/sigma)**2),
            'r--', linewidth=2, label='Normal Distribution')
    
    # Formatting
    ax.set_title(f'Return Distribution: {strategy_name}', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Daily Return (%)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.grid(True, alpha=0.3, linestyle='--', axis='y')
    
    # Add statistics box
    stats_text = f'Mean: {mu:.3f}%\nStd Dev: {sigma:.3f}%\nSkew: {returns.skew():.3f}\nKurtosis: {returns.kurtosis():.3f}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.legend()
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved returns distribution to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_rolling_sharpe(df: pd.DataFrame, 
                        window: int = 252,
                        strategy_name: str = "Strategy",
                        save_path: Optional[str] = None) -> None:
    """
    Plot rolling Sharpe ratio.
    
    Args:
        df: DataFrame with Strategy_Return column
        window: Rolling window in days (default 252 = 1 year)
        strategy_name: Name of the strategy
        save_path: Path to save the figure
    """
    returns = df['Strategy_Return'].dropna()
    
    # Calculate rolling Sharpe (annualized)
    rolling_mean = returns.rolling(window).mean() * 252
    rolling_std = returns.rolling(window).std() * np.sqrt(252)
    rolling_sharpe = (rolling_mean - 0.06) / rolling_std  # 6% risk-free rate
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Plot rolling Sharpe
    ax.plot(rolling_sharpe.index, rolling_sharpe, 
            color='#2E86AB', linewidth=2, label=f'{window}-day Rolling Sharpe')
    ax.axhline(y=1.0, color='green', linestyle='--', linewidth=1.5, 
               label='Sharpe = 1.0 (Good)', alpha=0.7)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=1.5, 
               label='Sharpe = 0 (No Edge)', alpha=0.7)
    
    # Formatting
    ax.set_title(f'Rolling Sharpe Ratio: {strategy_name}', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Sharpe Ratio', fontsize=12)
    ax.legend(loc='best', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved rolling Sharpe to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_monthly_returns_heatmap(df: pd.DataFrame, 
                                  strategy_name: str = "Strategy",
                                  save_path: Optional[str] = None) -> None:
    """
    Plot monthly returns heatmap.
    
    Args:
        df: DataFrame with Strategy_Return column
        strategy_name: Name of the strategy
        save_path: Path to save the figure
    """
    returns = df['Strategy_Return'].dropna()
    
    # Calculate monthly returns
    monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100
    
    # Pivot to year x month format
    monthly_returns_df = pd.DataFrame({
        'Year': monthly_returns.index.year,
        'Month': monthly_returns.index.month,
        'Return': monthly_returns.values
    })
    
    pivot_table = monthly_returns_df.pivot(index='Year', columns='Month', values='Return')
    
    # Month names
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    pivot_table.columns = month_names
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Heatmap
    sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='RdYlGn', center=0,
                cbar_kws={'label': 'Monthly Return (%)'},
                linewidths=0.5, linecolor='gray', ax=ax)
    
    # Formatting
    ax.set_title(f'Monthly Returns Heatmap: {strategy_name}', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Year', fontsize=12)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved monthly returns heatmap to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_strategy_comparison(results_dict: dict, 
                              save_path: Optional[str] = None) -> None:
    """
    Plot multiple strategies on the same chart.
    
    Args:
        results_dict: Dict of {strategy_name: df} with equity curves
        save_path: Path to save the figure
    """
    fig, ax = plt.subplots(figsize=(14, 7))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6A994E']
    
    for i, (name, df) in enumerate(results_dict.items()):
        ax.plot(df.index, df['Strategy_Equity'], 
                label=name, linewidth=2, color=colors[i % len(colors)], alpha=0.8)
    
    # Formatting
    ax.set_title('Strategy Comparison: Equity Curves', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Portfolio Value (₹)', fontsize=12)
    ax.legend(loc='upper left', frameon=True, shadow=True)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved strategy comparison to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_trade_analysis(trades_df: pd.DataFrame, 
                        strategy_name: str = "Strategy",
                        save_path: Optional[str] = None) -> None:
    """
    Plot trade-level analysis.
    
    Args:
        trades_df: DataFrame with trade log
        strategy_name: Name of the strategy
        save_path: Path to save the figure
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 1. P&L distribution
    axes[0, 0].hist(trades_df['PnL'], bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
    axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0, 0].set_title('Trade P&L Distribution', fontweight='bold')
    axes[0, 0].set_xlabel('P&L (₹)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].grid(True, alpha=0.3, axis='y')
    
    # 2. Return % distribution
    axes[0, 1].hist(trades_df['Return_Pct'] * 100, bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
    axes[0, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0, 1].set_title('Trade Return % Distribution', fontweight='bold')
    axes[0, 1].set_xlabel('Return (%)')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].grid(True, alpha=0.3, axis='y')
    
    # 3. Trade duration
    trades_df['Duration'] = (pd.to_datetime(trades_df['Exit_Date']) - 
                              pd.to_datetime(trades_df['Entry_Date'])).dt.days
    axes[1, 0].hist(trades_df['Duration'], bins=30, color='#F18F01', alpha=0.7, edgecolor='black')
    axes[1, 0].set_title('Trade Duration Distribution', fontweight='bold')
    axes[1, 0].set_xlabel('Duration (days)')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].grid(True, alpha=0.3, axis='y')
    
    # 4. Cumulative P&L
    trades_df['Cumulative_PnL'] = trades_df['PnL'].cumsum()
    axes[1, 1].plot(range(len(trades_df)), trades_df['Cumulative_PnL'], 
                    color='#2E86AB', linewidth=2)
    axes[1, 1].set_title('Cumulative P&L by Trade', fontweight='bold')
    axes[1, 1].set_xlabel('Trade Number')
    axes[1, 1].set_ylabel('Cumulative P&L (₹)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle(f'Trade Analysis: {strategy_name}', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved trade analysis to {save_path}")
    else:
        plt.show()
    
    plt.close()


def generate_all_plots(df: pd.DataFrame, 
                       trades_df: pd.DataFrame,
                       strategy_name: str = "Strategy",
                       output_dir: str = "outputs/") -> None:
    """
    Generate all standard plots for a backtest.
    
    Args:
        df: Results DataFrame with returns and equity
        trades_df: Trade log DataFrame
        strategy_name: Name of the strategy
        output_dir: Directory to save plots
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"Generating plots for {strategy_name}...")
    print(f"{'='*60}\n")
    
    # Generate all plots
    plot_equity_curve(df, strategy_name, f"{output_dir}/equity_curve.png")
    plot_drawdown(df, strategy_name, f"{output_dir}/drawdown.png")
    plot_returns_distribution(df, strategy_name, f"{output_dir}/returns_distribution.png")
    plot_rolling_sharpe(df, 252, strategy_name, f"{output_dir}/rolling_sharpe.png")
    plot_monthly_returns_heatmap(df, strategy_name, f"{output_dir}/monthly_heatmap.png")
    plot_trade_analysis(trades_df, strategy_name, f"{output_dir}/trade_analysis.png")
    
    print(f"\n{'='*60}")
    print(f"All plots saved to {output_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    print("Plots module loaded successfully.")
    print("Use generate_all_plots() to create comprehensive visualizations.")
