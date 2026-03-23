"""Qualifying page - sector gap waterfall chart."""

import pandas as pd
import streamlit as st
from db import get_seasons, get_events, get_laps, get_results
from charts import qualifying_waterfall
from style import PLOTLY_CONFIG, section_header, get_team_color
from config import TEAM_COLORS

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

# Custom HTML qualifying results table
if not results.empty:
    top_results = results.sort_values("position").head(10)

    def _format_lap(ms):
        if pd.notna(ms):
            return f"{int(ms // 60000)}:{(ms % 60000) / 1000:06.3f}"
        return "-"

    # Build position badge color: P1 gold, P2 silver, P3 bronze, rest muted
    def _pos_color(pos):
        colors = {1: "#E10600", 2: "#A0A0B0", 3: "#CD7F32"}
        return colors.get(pos, "#3A3A4A")

    rows_html = ""
    for _, row in top_results.iterrows():
        pos = int(row["position"])
        driver = row["driver"]
        team = row["team"]
        lap_ms = row.get("best_lap_ms")
        lap_str = _format_lap(lap_ms)
        team_color = get_team_color(team)
        badge_bg = _pos_color(pos)

        rows_html += f"""
        <tr>
            <td><span class="pos-badge" style="background:{badge_bg}">{pos}</span></td>
            <td>
                <span class="team-indicator" style="background:{team_color}"></span>
                {driver}
            </td>
            <td class="text-muted">{team}</td>
            <td class="mono">{lap_str}</td>
        </tr>
        """

    table_html = f"""
    <table class="f1-table">
        <thead>
            <tr>
                <th style="width:50px">Pos</th>
                <th>Driver</th>
                <th>Team</th>
                <th style="width:130px">Best Lap</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
    """
    st.markdown(table_html, unsafe_allow_html=True)

# Waterfall chart
st.markdown(section_header("Sector Gaps to Pole"), unsafe_allow_html=True)
st.plotly_chart(
    qualifying_waterfall(laps, results, title=f"{event_name} - Sector Gaps to Pole"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)
