"""Qualifying page - sector gap waterfall chart."""

import pandas as pd
import streamlit as st
from db import get_seasons, get_events, get_laps, get_results
from charts import qualifying_waterfall
from style import PLOTLY_CONFIG

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

# Top qualifying results table
if not results.empty:
    top_results = results.sort_values("position").head(10)[["position", "driver", "team", "best_lap_ms"]]
    top_results["best_lap"] = top_results["best_lap_ms"].apply(
        lambda ms: f"{int(ms // 60000)}:{(ms % 60000) / 1000:06.3f}" if pd.notna(ms) else "-"
    )
    st.dataframe(
        top_results[["position", "driver", "team", "best_lap"]].rename(columns={
            "position": "Pos", "driver": "Driver", "team": "Team", "best_lap": "Best Lap"
        }),
        hide_index=True,
        use_container_width=True,
    )

st.divider()

# Waterfall chart
st.plotly_chart(
    qualifying_waterfall(laps, results, title=f"{event_name} - Sector Gaps to Pole"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)
