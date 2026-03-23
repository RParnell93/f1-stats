"""F1 Stats - main Streamlit entrypoint."""

import streamlit as st

st.set_page_config(
    page_title="F1 Stats",
    page_icon=":racing_car:",
    layout="wide",
    initial_sidebar_state="expanded",
)

from style import APP_CSS

st.markdown(APP_CSS, unsafe_allow_html=True)

# Branded header
st.markdown("""
<div class="f1-header">
    <span class="f1-header-title">F1 <span class="f1-header-accent">STATS</span></span>
</div>
<div class="f1-header-bar"></div>
<div class="f1-tagline">Live timing data & race analytics</div>
""", unsafe_allow_html=True)

pages = [
    st.Page("pages/race_analysis.py", title="Race Analysis", icon=":material/speed:"),
    st.Page("pages/qualifying.py", title="Qualifying", icon=":material/timer:"),
    st.Page("pages/season_overview.py", title="Season Overview", icon=":material/leaderboard:"),
]

nav = st.navigation(pages)
nav.run()
