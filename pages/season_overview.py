"""Season Overview page - championship standings progression."""

import streamlit as st
from db import get_seasons, get_standings
from charts import championship_progression
from style import PLOTLY_CONFIG

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
st.plotly_chart(
    championship_progression(standings, title=f"{season} Drivers' Championship"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)

st.divider()

# Current standings table
latest_round = standings["round"].max()
current = standings[standings["round"] == latest_round].sort_values("position")

st.subheader(f"Standings after Round {latest_round}")
st.dataframe(
    current[["position", "driver", "team", "points", "wins"]].rename(columns={
        "position": "Pos", "driver": "Driver", "team": "Team",
        "points": "Points", "wins": "Wins",
    }),
    hide_index=True,
    use_container_width=True,
)
