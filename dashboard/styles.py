"""
Professional Dark Theme Design System
Bloomberg Terminal-Inspired Analytics Platform
"""

# Dark Theme Color Palette (High Contrast)
COLORS = {
    # Backgrounds
    'bg_primary': '#0E1117',    # Streamlit dark default
    'bg_card': '#262730',       # Card background (slightly lighter)
    'bg_hover': '#2E3039',      # Hover state
    
    # Text
    'text_primary': '#FAFAFA',   # Almost white - main text
    'text_secondary': '#A3A8B8', # Light gray - secondary text
    'text_muted': '#64748B',     # Muted gray - labels
    
    # Accent colors
    'accent': '#00D4FF',         # Bright cyan - Bloomberg style
    'accent_dark': '#0099CC',    # Darker cyan for hover
    
    # Status colors (bright for dark theme)
    'success': '#00C853',        # Bright green
    'warning': '#FFB300',        # Bright amber
    'danger': '#FF5252',         # Bright red
    
    # Chart colors
    'chart_primary': '#00D4FF',  # Cyan
    'chart_secondary': '#A3A8B8', # Gray
    'chart_positive': '#00C853',  # Green
    'chart_negative': '#FF5252',  # Red
}

# Minimal CSS - Work WITH Streamlit's dark theme
CUSTOM_CSS = """
<style>
    /* Remove default Streamlit padding for cleaner look */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Headers - Light text */
    h1, h2, h3, h4, h5, h6 {
        color: #FAFAFA !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 2rem !important;
        border-bottom: 3px solid #00D4FF;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        font-size: 1.5rem !important;
        margin-top: 2rem;
    }
    
    h3 {
        font-size: 1.25rem !important;
        color: #A3A8B8 !important;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #262730;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #00D4FF;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        transition: all 0.2s;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,212,255,0.2);
        transform: translateY(-2px);
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        color: #FAFAFA;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-delta {
        font-size: 0.875rem;
        font-weight: 600;
    }
    
    .metric-delta.positive {
        color: #00C853;
    }
    
    .metric-delta.negative {
        color: #FF5252;
    }
    
    /* Alert Banners */
    .alert-banner {
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .alert-success {
        background: rgba(0, 200, 83, 0.1);
        border-color: #00C853;
        color: #00C853;
    }
    
    .alert-warning {
        background: rgba(255, 179, 0, 0.1);
        border-color: #FFB300;
        color: #FFB300;
    }
    
    .alert-danger {
        background: rgba(255, 82, 82, 0.1);
        border-color: #FF5252;
        color: #FF5252;
    }
    
    /* Insight List */
    .insight-list {
        background: #262730;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #2E3039;
    }
    
    .insight-list ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .insight-list li {
        padding: 0.75rem 0;
        color: #FAFAFA;
        font-size: 1rem;
        line-height: 1.6;
        border-bottom: 1px solid #2E3039;
    }
    
    .insight-list li:last-child {
        border-bottom: none;
    }
    
    .insight-list li:before {
        content: "▸";
        color: #00D4FF;
        font-weight: bold;
        margin-right: 0.75rem;
        font-size: 1.2rem;
    }
    
    /* Streamlit metric overrides */
    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stMetricValue"] {
        color: #FAFAFA !important;
        font-size: 1.75rem !important;
    }
    
    [data-testid="stMetricDelta"] {
        color: #00C853 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #262730;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        color: #A3A8B8;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #0E1117;
        color: #00D4FF;
        border-bottom: 3px solid #00D4FF;
    }
    
    /* Dataframe styling */
    .dataframe {
        color: #FAFAFA !important;
    }
    
    /* Section divider */
    .section-divider {
        border-top: 1px solid #2E3039;
        margin: 2rem 0;
    }
</style>
"""

def get_alert_class(cagr, sharpe):
    """Determine alert banner class based on performance."""
    if cagr > 0.15 and sharpe > 1.0:
        return 'alert-success'
    elif cagr > 0 and sharpe > 0:
        return 'alert-warning'
    else:
        return 'alert-danger'

def get_alert_message(cagr, sharpe):
    """Get alert message based on performance."""
    if cagr > 0.15 and sharpe > 1.0:
        return "✓ <strong>Strong Performance:</strong> Strategy significantly outperforms benchmark with excellent risk-adjusted returns."
    elif cagr > 0 and sharpe > 0:
        return "⚠ <strong>Moderate Performance:</strong> Strategy shows positive returns but requires monitoring."
    else:
        return "✗ <strong>Underperformance:</strong> Strategy underperforms benchmark. Review parameters."

def format_metric_delta(value, benchmark_value, is_higher_better=True):
    """Format metric delta with arrow and color."""
    diff = value - benchmark_value
    
    if is_higher_better:
        is_positive = diff > 0
    else:
        is_positive = diff < 0
    
    arrow = "↑" if is_positive else "↓"
    css_class = "positive" if is_positive else "negative"
    
    return arrow, css_class, abs(diff)
