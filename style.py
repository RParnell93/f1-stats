"""Plotly chart template and CSS for the Streamlit app."""

import plotly.graph_objects as go
from config import (
    BG_PRIMARY, TEXT_PRIMARY, TEXT_SECONDARY, GRID_COLOR, F1_RED,
    TEAM_COLORS, COMPOUND_COLORS, POSITIVE, NEGATIVE,
)

# Plotly layout template applied to every chart
F1_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=BG_PRIMARY,
        plot_bgcolor=BG_PRIMARY,
        font=dict(family="Inter, sans-serif", size=12, color=TEXT_SECONDARY),
        title=dict(font=dict(color=TEXT_PRIMARY, size=16)),
        xaxis=dict(gridcolor=GRID_COLOR, gridwidth=1, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, gridwidth=1, zerolinecolor=GRID_COLOR),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_SECONDARY)),
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


# Custom CSS injected into Streamlit
APP_CSS = """
<style>
    /* Metric cards */
    .metric-card {
        background: #1A1D24;
        border: 1px solid #3D4150;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .metric-card .value {
        font-size: clamp(1.3rem, 4vw, 2rem);
        font-weight: 700;
        color: #FAFAFA;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #A3A8B4;
        margin-top: 0.25rem;
    }
    /* Mobile tweaks */
    @media (max-width: 768px) {
        .metric-card .value {
            font-size: 1.3rem;
        }
    }
</style>
"""
