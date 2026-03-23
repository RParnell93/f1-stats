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

# Current standings as styled HTML table
latest_round = standings["round"].max()
current = standings[standings["round"] == latest_round].sort_values("position")

st.markdown(section_header(f"Standings after Round {latest_round}"), unsafe_allow_html=True)

def _pos_color(pos):
    return {1: "#E10600", 2: "#A0A0B0", 3: "#CD7F32"}.get(pos, "#3A3A4A")

_th = "font-family:Titillium Web,sans-serif;font-weight:600;text-transform:uppercase;letter-spacing:1.5px;font-size:0.7rem;color:#6B6B7B;padding:0.6rem 0.8rem;border-bottom:1px solid #3A3A4A;text-align:left;"
_td = "padding:0.55rem 0.8rem;border-bottom:1px solid #2A2A3A;color:#FFFFFF;font-family:Inter,sans-serif;font-size:0.88rem;"
_badge = "display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;font-family:JetBrains Mono,monospace;font-weight:700;font-size:0.75rem;color:#FFFFFF;"
_team_bar = "display:inline-block;width:4px;height:20px;border-radius:2px;margin-right:8px;vertical-align:middle;"
_mono = "font-family:JetBrains Mono,monospace;"
_muted = "color:#6B6B7B;"

rows_html = ""
for _, row in current.iterrows():
    pos = int(row["position"])
    driver = row["driver"]
    team = row["team"]
    points = int(row["points"]) if row["points"] == int(row["points"]) else row["points"]
    wins = int(row["wins"]) if "wins" in row and row["wins"] == int(row["wins"]) else row.get("wins", 0)
    team_color = get_team_color(team)
    badge_bg = _pos_color(pos)

    rows_html += f"""<tr style="transition:background 0.15s;" onmouseover="this.style.background='#22222E'" onmouseout="this.style.background='transparent'">
        <td style="{_td}"><span style="{_badge}background:{badge_bg};">{pos}</span></td>
        <td style="{_td}font-weight:600;"><span style="{_team_bar}background:{team_color};"></span>{driver}</td>
        <td style="{_td}{_muted}">{team}</td>
        <td style="{_td}{_mono}font-weight:700;">{points}</td>
        <td style="{_td}{_mono}">{wins}</td>
    </tr>"""

st.html(f"""
<link href="https://fonts.googleapis.com/css2?family=Titillium+Web:wght@600;700&family=JetBrains+Mono:wght@400;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<table style="width:100%;border-collapse:collapse;background:#15151E;">
    <thead><tr>
        <th style="{_th}width:50px;">Pos</th>
        <th style="{_th}">Driver</th>
        <th style="{_th}">Team</th>
        <th style="{_th}width:80px;">Points</th>
        <th style="{_th}width:60px;">Wins</th>
    </tr></thead>
    <tbody>{rows_html}</tbody>
</table>
""")
