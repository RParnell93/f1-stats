"""Season Overview page - championship standings progression."""

import streamlit as st
from db import get_seasons, get_standings
from charts import championship_progression
from style import PLOTLY_CONFIG, section_header, get_team_color

st.title("Season Overview")

# Sidebar filters
seasons = get_seasons()
if seasons.empty:
    st.warning("No data loaded yet. Run the pipeline first: `python snapshot.py`")
    st.stop()

season = st.sidebar.selectbox("Season", seasons["season"].tolist(), key="s_season")

standings = get_standings(season)

if standings.empty:
    st.info("No standings data available for this season.")
    st.stop()

st.subheader(f"{season} Championship")

# Championship chart
st.markdown(section_header("Points Progression"), unsafe_allow_html=True)
st.plotly_chart(
    championship_progression(standings, title=f"{season} Drivers' Championship"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)

# Current standings as custom HTML table
latest_round = standings["round"].max()
current = standings[standings["round"] == latest_round].sort_values("position")

st.markdown(section_header(f"Standings after Round {latest_round}"), unsafe_allow_html=True)

# Build position badge colors
def _pos_color(pos):
    colors = {1: "#E10600", 2: "#A0A0B0", 3: "#CD7F32"}
    return colors.get(pos, "#3A3A4A")

rows_html = ""
for _, row in current.iterrows():
    pos = int(row["position"])
    driver = row["driver"]
    team = row["team"]
    points = int(row["points"]) if row["points"] == int(row["points"]) else row["points"]
    wins = int(row["wins"]) if "wins" in row and row["wins"] == int(row["wins"]) else row.get("wins", 0)
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
        <td class="mono">{points}</td>
        <td class="mono">{wins}</td>
    </tr>
    """

table_html = f"""
<table class="f1-table">
    <thead>
        <tr>
            <th style="width:50px">Pos</th>
            <th>Driver</th>
            <th>Team</th>
            <th style="width:80px">Points</th>
            <th style="width:60px">Wins</th>
        </tr>
    </thead>
    <tbody>{rows_html}</tbody>
</table>
"""
st.markdown(table_html, unsafe_allow_html=True)
