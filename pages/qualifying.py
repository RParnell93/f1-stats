"""Qualifying page - sector gap waterfall chart."""

import pandas as pd
import streamlit as st
from db import get_seasons, get_events, get_laps, get_results
from charts import qualifying_waterfall
from style import PLOTLY_CONFIG, section_header, get_team_color

st.title("Qualifying Analysis")

# Sidebar filters
seasons = get_seasons()
if seasons.empty:
    st.warning("No data loaded yet. Run the pipeline first: `python snapshot.py`")
    st.stop()

season = st.sidebar.selectbox("Season", seasons["season"].tolist(), key="q_season")
events = get_events(season)

if events.empty:
    st.info("No events found for this season.")
    st.stop()

event_options = {f"R{row['round']}: {row['event_name']}": row["round"] for _, row in events.iterrows()}
selected_event = st.sidebar.selectbox("Grand Prix", list(event_options.keys()), key="q_event")
round_num = event_options[selected_event]

# Load qualifying data
laps = get_laps(season, round_num, "Q")
results = get_results(season, round_num, "Q")

if laps.empty:
    st.info("Qualifying data not available for this event.")
    st.stop()

event_name = events[events["round"] == round_num]["event_name"].iloc[0]
st.subheader(f"{event_name} {season} - Qualifying")

# Qualifying results table with inline styles (st.html for reliable rendering)
if not results.empty:
    top_results = results.sort_values("position").head(10)

    def _format_lap(ms):
        if pd.notna(ms):
            return f"{int(ms // 60000)}:{(ms % 60000) / 1000:06.3f}"
        return "-"

    def _pos_color(pos):
        return {1: "#E10600", 2: "#A0A0B0", 3: "#CD7F32"}.get(pos, "#3A3A4A")

    _th = "font-family:Titillium Web,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;font-size:0.7rem;color:#6B6B7B;padding:0.6rem 0.8rem;border-bottom:1px solid #3A3A4A;text-align:left;"
    _td = "padding:0.55rem 0.8rem;border-bottom:1px solid #2A2A3A;color:#FFFFFF;font-family:Inter,sans-serif;font-size:0.88rem;"
    _badge = "display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;font-family:JetBrains Mono,monospace;font-weight:700;font-size:0.75rem;color:#FFFFFF;"
    _team_bar = "display:inline-block;width:4px;height:20px;border-radius:2px;margin-right:8px;vertical-align:middle;"
    _mono = "font-family:JetBrains Mono,monospace;"
    _muted = "color:#6B6B7B;"

    rows_html = ""
    for _, row in top_results.iterrows():
        pos = int(row["position"])
        driver = row["driver"]
        team = row["team"]
        lap_str = _format_lap(row.get("best_lap_ms"))
        team_color = get_team_color(team)
        badge_bg = _pos_color(pos)

        rows_html += f"""<tr style="transition:background 0.15s;" onmouseover="this.style.background='#22222E'" onmouseout="this.style.background='transparent'">
            <td style="{_td}"><span style="{_badge}background:{badge_bg};">{pos}</span></td>
            <td style="{_td}font-weight:600;"><span style="{_team_bar}background:{team_color};"></span>{driver}</td>
            <td style="{_td}{_muted}">{team}</td>
            <td style="{_td}{_mono}">{lap_str}</td>
        </tr>"""

    st.html(f"""
    <link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@600;700&family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <table style="width:100%;border-collapse:collapse;background:#15151E;">
        <thead><tr>
            <th style="{_th}width:50px;">Pos</th>
            <th style="{_th}">Driver</th>
            <th style="{_th}">Team</th>
            <th style="{_th}width:130px;">Best Lap</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
    </table>
    """)

# Sector gap chart
st.markdown(section_header("Sector Gaps to Pole"), unsafe_allow_html=True)
st.plotly_chart(
    qualifying_waterfall(laps, results, title=f"{event_name} - Sector Gaps to Pole"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)
