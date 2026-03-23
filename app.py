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

pages = [
    st.Page("pages/race_analysis.py", title="Race Analysis", icon=":material/speed:"),
    st.Page("pages/qualifying.py", title="Qualifying", icon=":material/timer:"),
    st.Page("pages/season_overview.py", title="Season Overview", icon=":material/leaderboard:"),
]

nav = st.navigation(pages)
nav.run()
