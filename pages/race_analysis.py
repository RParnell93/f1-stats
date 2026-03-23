"""Race Analysis page - strategy timeline, position changes, pace distribution."""

import streamlit as st
from db import get_seasons, get_events, get_laps, get_results, get_pit_stops
from charts import strategy_timeline, position_changes, lap_time_distribution
from style import PLOTLY_CONFIG

st.title("Race Analysis")

# Sidebar filters
seasons = get_seasons()
if seasons.empty:
    st.warning("No data loaded yet. Run the pipeline first: `python snapshot.py`")
    st.stop()

season = st.sidebar.selectbox("Season", seasons["season"].tolist())
events = get_events(season)

if events.empty:
    st.info("No events found for this season.")
    st.stop()

event_options = {f"R{row['round']}: {row['event_name']}": row["round"] for _, row in events.iterrows()}
selected_event = st.sidebar.selectbox("Grand Prix", list(event_options.keys()))
round_num = event_options[selected_event]

# Load data
laps = get_laps(season, round_num, "R")
results = get_results(season, round_num, "R")

if laps.empty or results.empty:
    st.info("Race data not available for this event.")
    st.stop()

event_name = events[events["round"] == round_num]["event_name"].iloc[0]
st.subheader(f"{event_name} {season}")

# Metric cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    winner = results[results["position"] == 1]
    if not winner.empty:
        st.metric("Winner", winner.iloc[0]["driver"])
with col2:
    total_laps = int(laps["lap_number"].max()) if not laps.empty else 0
    st.metric("Total Laps", total_laps)
with col3:
    pit_stops = get_pit_stops(season, round_num)
    st.metric("Pit Stops", len(pit_stops))
with col4:
    dnfs = results[results["status"].str.contains("Retired|Accident|Collision|Engine|Gearbox|Hydraulic|Electrical", case=False, na=False)]
    st.metric("DNFs", len(dnfs))

st.divider()

# Strategy Timeline
st.plotly_chart(
    strategy_timeline(laps, results, title=f"{event_name} - Tire Strategy"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)

# Position Changes
st.plotly_chart(
    position_changes(laps, results, title=f"{event_name} - Position Changes"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)

# Lap Time Distribution
st.plotly_chart(
    lap_time_distribution(laps, results, title=f"{event_name} - Race Pace (Top 10)"),
    use_container_width=True,
    config=PLOTLY_CONFIG,
)
