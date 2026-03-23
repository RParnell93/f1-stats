"""Plotly chart template and CSS for the Streamlit app."""

import plotly.graph_objects as go
from config import (
    BG_PRIMARY, BG_CARD, BG_DEEP, TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED,
    GRID_COLOR, CARD_BORDER, F1_RED, TEAM_COLORS, COMPOUND_COLORS,
    POSITIVE, NEGATIVE,
)

# Plotly layout template applied to every chart
F1_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_PRIMARY,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_SECONDARY),
        title=dict(font=dict(
            family="Titillium Web, sans-serif",
            color=TEXT_PRIMARY,
            size=16,
            weight=700,
        )),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            gridwidth=1,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(family="JetBrains Mono, monospace", size=11),
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            gridwidth=1,
            zerolinecolor=GRID_COLOR,
            tickfont=dict(family="JetBrains Mono, monospace", size=11),
        ),
        legend=dict(
            bgcolor="rgba(30, 30, 46, 0.85)",
            bordercolor=CARD_BORDER,
            borderwidth=1,
            font=dict(color=TEXT_SECONDARY, size=11),
        ),
        margin=dict(l=50, r=20, t=60, b=50),
    )
)

# Standard Plotly config for all st.plotly_chart calls
PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}


def apply_template(fig):
    """Apply F1 dark theme to a Plotly figure."""
    fig.update_layout(template=F1_TEMPLATE)
    return fig


def get_team_color(team_name):
    """Get chart color for a team, with fallback."""
    return TEAM_COLORS.get(team_name, "#999999")


def get_compound_color(compound):
    """Get color for a tire compound."""
    return COMPOUND_COLORS.get(compound.upper(), "#999999")


# ---------------------------------------------------------------------------
# HTML helper: metric card
# ---------------------------------------------------------------------------
def metric_card(label, value, color=TEXT_PRIMARY):
    """Return HTML for a styled metric card."""
    return f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color:{color}">{value}</div>
    </div>
    """


def section_header(text):
    """Return HTML for an uppercase section header with red accent."""
    return f"""
    <div class="section-header">{text}</div>
    <div class="section-divider"></div>
    """


# ---------------------------------------------------------------------------
# Custom CSS injected into Streamlit
# ---------------------------------------------------------------------------
APP_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@400;600;700;900&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

    /* ── F1 Red accent stripe at top ── */
    .stApp::before {
        content: "";
        display: block;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #E10600 0%, #E10600 40%, transparent 100%);
        z-index: 9999;
    }

    /* ── Global typography overrides ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, h5, h6,
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        font-family: 'Titillium Web', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background-color: #1E1E2E !important;
        border-right: 1px solid #3A3A4A;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stRadio label {
        font-family: 'Titillium Web', sans-serif;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-size: 0.75rem;
        color: #A0A0B0;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #1E1E2E;
        border: 1px solid #3A3A4A;
        border-radius: 6px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-label {
        font-family: 'Titillium Web', sans-serif;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6B6B7B;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: clamp(1.3rem, 4vw, 1.8rem);
        font-weight: 700;
        color: #FFFFFF;
        overflow-wrap: break-word;
    }

    /* ── Section headers ── */
    .section-header {
        font-family: 'Titillium Web', sans-serif;
        font-weight: 700;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #A0A0B0;
        margin-top: 1.5rem;
        margin-bottom: 0.4rem;
    }

    /* ── Section dividers - red fade ── */
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, #E10600 0%, #E1060040 30%, transparent 60%);
        margin-bottom: 1rem;
        border: none;
    }

    /* ── Streamlit native metric override ── */
    div[data-testid="stMetric"] {
        background: #1E1E2E;
        border: 1px solid #3A3A4A;
        border-radius: 6px;
        padding: 0.8rem;
    }
    div[data-testid="stMetric"] label {
        font-family: 'Titillium Web', sans-serif !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.7rem !important;
        color: #6B6B7B !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-weight: 700;
    }

    /* ── Dataframes / tables ── */
    .stDataFrame {
        border: 1px solid #3A3A4A;
        border-radius: 6px;
        overflow: hidden;
    }
    .stDataFrame [data-testid="stDataFrameResizable"] {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }

    /* ── Branded header ── */
    .f1-header {
        display: flex;
        align-items: baseline;
        gap: 0.75rem;
        margin-bottom: 0.15rem;
    }
    .f1-header-title {
        font-family: 'Titillium Web', sans-serif;
        font-weight: 900;
        font-size: clamp(1.6rem, 5vw, 2.2rem);
        color: #FFFFFF;
        letter-spacing: 2px;
    }
    .f1-header-accent {
        color: #E10600;
    }
    .f1-header-bar {
        height: 3px;
        width: 80px;
        background: #E10600;
        margin-bottom: 0.2rem;
        border-radius: 2px;
    }
    .f1-tagline {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        color: #6B6B7B;
        margin-bottom: 1.5rem;
        letter-spacing: 0.3px;
    }

    /* ── Custom HTML table (qualifying / standings) ── */
    .f1-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
    }
    .f1-table th {
        font-family: 'Titillium Web', sans-serif;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-size: 0.7rem;
        color: #6B6B7B;
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid #3A3A4A;
        text-align: left;
    }
    .f1-table td {
        padding: 0.55rem 0.8rem;
        border-bottom: 1px solid #2A2A3A;
        color: #FFFFFF;
    }
    .f1-table tr:hover td {
        background: #22222E;
    }
    .f1-table .pos-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 50%;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.75rem;
        color: #FFFFFF;
    }
    .f1-table .team-indicator {
        display: inline-block;
        width: 4px;
        height: 20px;
        border-radius: 2px;
        margin-right: 8px;
        vertical-align: middle;
    }
    .f1-table .mono {
        font-family: 'JetBrains Mono', monospace;
    }
    .f1-table .text-muted {
        color: #6B6B7B;
    }

    /* ── Position change arrows ── */
    .pos-up { color: #22C55E; font-size: 0.75rem; }
    .pos-down { color: #EF4444; font-size: 0.75rem; }
    .pos-same { color: #6B6B7B; font-size: 0.75rem; }

    /* ── Hide default Streamlit divider, use ours ── */
    hr {
        border-color: #2A2A3A !important;
        opacity: 0.5;
    }

    /* ── Mobile tweaks ── */
    @media (max-width: 768px) {
        .metric-value {
            font-size: 1.2rem;
        }
        .f1-header-title {
            font-size: 1.4rem;
        }
        .f1-table {
            font-size: 0.8rem;
        }
        .f1-table th, .f1-table td {
            padding: 0.4rem 0.5rem;
        }
    }
</style>
"""
