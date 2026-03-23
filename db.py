"""MotherDuck connection and query helpers."""

import os
import duckdb
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "f1_stats"


def _get_token():
    """Get MotherDuck token from env or Streamlit secrets."""
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        try:
            token = st.secrets["MOTHERDUCK_TOKEN"]
        except Exception:
            pass
    return token


@st.cache_resource(ttl=3600)
def get_connection():
    """Get a cached MotherDuck connection."""
    token = _get_token()
    if not token:
        raise ValueError("MOTHERDUCK_TOKEN not found in env or Streamlit secrets")
    return duckdb.connect(f"md:{DB_NAME}?motherduck_token={token}")


def get_connection_raw():
    """Get a MotherDuck connection without Streamlit caching (for pipelines)."""
    token = _get_token()
    if not token:
        raise ValueError("MOTHERDUCK_TOKEN not found")
    return duckdb.connect(f"md:{DB_NAME}?motherduck_token={token}")


@st.cache_data(ttl=900)
def get_seasons():
    """Get list of available seasons."""
    con = get_connection()
    return con.execute(
        "SELECT DISTINCT season FROM sessions ORDER BY season DESC"
    ).df()


@st.cache_data(ttl=900)
def get_events(season):
    """Get events for a season."""
    con = get_connection()
    return con.execute("""
        SELECT DISTINCT round, event_name, circuit_name
        FROM sessions
        WHERE season = ?
        ORDER BY round
    """, [season]).df()


@st.cache_data(ttl=900)
def get_session_types(season, round_num):
    """Get available session types for an event."""
    con = get_connection()
    return con.execute("""
        SELECT DISTINCT session_type
        FROM sessions
        WHERE season = ? AND round = ?
        ORDER BY session_type
    """, [season, round_num]).df()


@st.cache_data(ttl=900)
def get_laps(season, round_num, session_type):
    """Get lap data for a session."""
    con = get_connection()
    return con.execute("""
        SELECT * FROM laps
        WHERE season = ? AND round = ? AND session_type = ?
        ORDER BY driver, lap_number
    """, [season, round_num, session_type]).df()


@st.cache_data(ttl=900)
def get_results(season, round_num, session_type):
    """Get results for a session."""
    con = get_connection()
    return con.execute("""
        SELECT * FROM results
        WHERE season = ? AND round = ? AND session_type = ?
        ORDER BY position
    """, [season, round_num, session_type]).df()


@st.cache_data(ttl=900)
def get_pit_stops(season, round_num):
    """Get pit stops for a race."""
    con = get_connection()
    return con.execute("""
        SELECT * FROM pit_stops
        WHERE season = ? AND round = ?
        ORDER BY lap_number, driver
    """, [season, round_num]).df()


@st.cache_data(ttl=3600)
def get_standings(season):
    """Get championship standings for a season."""
    con = get_connection()
    return con.execute("""
        SELECT * FROM standings
        WHERE season = ?
        ORDER BY round, position
    """, [season]).df()
