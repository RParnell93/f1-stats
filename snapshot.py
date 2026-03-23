"""Pipeline: FastF1 -> MotherDuck. Run via GitHub Actions or locally."""

import os
import sys
import fastf1
import duckdb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

DB_NAME = "f1_stats"
CACHE_DIR = os.environ.get("FASTF1_CACHE", "fastf1_cache")
SEASON = int(os.environ.get("F1_SEASON", "2026"))

# Session types to load
SESSION_TYPES = ["FP1", "FP2", "FP3", "Q", "R"]


def get_connection():
    token = os.environ.get("MOTHERDUCK_TOKEN")
    if not token:
        print("ERROR: MOTHERDUCK_TOKEN not set")
        sys.exit(1)
    return duckdb.connect(f"md:{DB_NAME}?motherduck_token={token}")


def create_tables(con):
    """Create tables if they don't exist."""
    con.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            season INTEGER,
            round INTEGER,
            event_name VARCHAR,
            session_type VARCHAR,
            session_date TIMESTAMP,
            circuit_name VARCHAR,
            circuit_key VARCHAR,
            PRIMARY KEY (season, round, session_type)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS laps (
            season INTEGER,
            round INTEGER,
            session_type VARCHAR,
            driver VARCHAR,
            lap_number INTEGER,
            lap_time_ms BIGINT,
            sector1_ms BIGINT,
            sector2_ms BIGINT,
            sector3_ms BIGINT,
            compound VARCHAR,
            tyre_life INTEGER,
            is_personal_best BOOLEAN,
            track_status VARCHAR,
            deleted BOOLEAN,
            pit_in BOOLEAN,
            pit_out BOOLEAN,
            position DOUBLE,
            PRIMARY KEY (season, round, session_type, driver, lap_number)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS results (
            season INTEGER,
            round INTEGER,
            session_type VARCHAR,
            position INTEGER,
            driver VARCHAR,
            team VARCHAR,
            grid_position INTEGER,
            status VARCHAR,
            points DOUBLE,
            fastest_lap BOOLEAN,
            best_lap_ms BIGINT,
            PRIMARY KEY (season, round, session_type, driver)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS pit_stops (
            season INTEGER,
            round INTEGER,
            driver VARCHAR,
            lap_number INTEGER,
            pit_duration_ms BIGINT,
            compound_before VARCHAR,
            compound_after VARCHAR,
            PRIMARY KEY (season, round, driver, lap_number)
        )
    """)
    con.execute("""
        CREATE TABLE IF NOT EXISTS standings (
            season INTEGER,
            round INTEGER,
            driver VARCHAR,
            team VARCHAR,
            points DOUBLE,
            position INTEGER,
            wins INTEGER,
            PRIMARY KEY (season, round, driver)
        )
    """)


def session_already_loaded(con, season, round_num, session_type):
    """Check if a session is already in MotherDuck."""
    result = con.execute("""
        SELECT COUNT(*) FROM sessions
        WHERE season = ? AND round = ? AND session_type = ?
    """, [season, round_num, session_type]).fetchone()
    return result[0] > 0


def td_to_ms(td):
    """Convert pandas Timedelta to milliseconds (int), or None."""
    if pd.isna(td):
        return None
    return int(td.total_seconds() * 1000)


def load_session(con, season, round_num, event_name, session_type):
    """Load a single session from FastF1 into MotherDuck."""
    if session_already_loaded(con, season, round_num, session_type):
        print(f"  Skipping {event_name} {session_type} (already loaded)")
        return

    print(f"  Loading {event_name} {session_type}...")
    try:
        session = fastf1.get_session(season, round_num, session_type)
        session.load(telemetry=False, weather=False, messages=False)
    except Exception as e:
        print(f"  ERROR loading {event_name} {session_type}: {e}")
        return

    # Insert session metadata
    session_date = session.date if hasattr(session, "date") else None
    circuit_name = session.event.get("CircuitName", "") if hasattr(session, "event") else ""
    circuit_key = session.event.get("CircuitKey", "") if hasattr(session, "event") else ""

    con.execute("""
        INSERT OR REPLACE INTO sessions VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [season, round_num, event_name, session_type, session_date, circuit_name, str(circuit_key)])

    # Insert laps
    laps = session.laps
    if laps is not None and not laps.empty:
        rows = []
        for _, lap in laps.iterrows():
            rows.append((
                season, round_num, session_type,
                lap.get("Driver", ""),
                int(lap.get("LapNumber", 0)),
                td_to_ms(lap.get("LapTime")),
                td_to_ms(lap.get("Sector1Time")),
                td_to_ms(lap.get("Sector2Time")),
                td_to_ms(lap.get("Sector3Time")),
                lap.get("Compound", "UNKNOWN"),
                int(lap["TyreLife"]) if pd.notna(lap.get("TyreLife")) else None,
                bool(lap.get("IsPersonalBest", False)),
                str(lap.get("TrackStatus", "")),
                bool(lap.get("Deleted", False)) if pd.notna(lap.get("Deleted")) else False,
                pd.notna(lap.get("PitInTime")),
                pd.notna(lap.get("PitOutTime")),
                float(lap["Position"]) if pd.notna(lap.get("Position")) else None,
            ))
        if rows:
            con.executemany("""
                INSERT OR REPLACE INTO laps VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, rows)
            print(f"    {len(rows)} laps inserted")

    # Insert results
    results = session.results
    if results is not None and not results.empty:
        rows = []
        for _, r in results.iterrows():
            best_lap = td_to_ms(r.get("Time")) if session_type == "R" else td_to_ms(r.get("Q3", r.get("Q2", r.get("Q1"))))
            rows.append((
                season, round_num, session_type,
                int(r["Position"]) if pd.notna(r.get("Position")) else None,
                r.get("Abbreviation", ""),
                r.get("TeamName", ""),
                int(r["GridPosition"]) if pd.notna(r.get("GridPosition")) else None,
                str(r.get("Status", "")),
                float(r["Points"]) if pd.notna(r.get("Points")) else 0.0,
                False,
                best_lap,
            ))
        if rows:
            con.executemany("""
                INSERT OR REPLACE INTO results VALUES (?,?,?,?,?,?,?,?,?,?,?)
            """, rows)
            print(f"    {len(rows)} results inserted")

    print(f"  Done: {event_name} {session_type}")


def load_standings(con, season, round_num, event_name):
    """Load championship standings after a race."""
    try:
        ergast = fastf1.ergast.Ergast()
        standings = ergast.get_driver_standings(season=season, round=round_num)
        if standings.content and len(standings.content) > 0:
            df = standings.content[0]
            rows = []
            for _, r in df.iterrows():
                rows.append((
                    season, round_num,
                    r.get("driverCode", r.get("givenName", "")),
                    r.get("constructorNames", [""])[0] if isinstance(r.get("constructorNames"), list) else str(r.get("constructorNames", "")),
                    float(r["points"]) if pd.notna(r.get("points")) else 0.0,
                    int(r["position"]) if pd.notna(r.get("position")) else 0,
                    int(r["wins"]) if pd.notna(r.get("wins")) else 0,
                ))
            if rows:
                con.executemany("""
                    INSERT OR REPLACE INTO standings VALUES (?,?,?,?,?,?,?)
                """, rows)
                print(f"  {len(rows)} standings rows inserted for round {round_num}")
    except Exception as e:
        print(f"  WARNING: Could not load standings for round {round_num}: {e}")


def main():
    print(f"F1 Stats Pipeline - Season {SEASON}")
    print("=" * 50)

    # Enable FastF1 cache
    os.makedirs(CACHE_DIR, exist_ok=True)
    fastf1.Cache.enable_cache(CACHE_DIR)

    con = get_connection()
    create_tables(con)

    # Get schedule
    schedule = fastf1.get_event_schedule(SEASON)
    # Filter to actual race events (exclude testing)
    races = schedule[schedule["EventFormat"].notna() & (schedule["RoundNumber"] > 0)]

    for _, event in races.iterrows():
        round_num = int(event["RoundNumber"])
        event_name = event["EventName"]
        print(f"\nRound {round_num}: {event_name}")

        for st in SESSION_TYPES:
            try:
                load_session(con, SEASON, round_num, event_name, st)
            except Exception as e:
                print(f"  ERROR: {st} - {e}")

        # Load standings after race
        if session_already_loaded(con, SEASON, round_num, "R"):
            load_standings(con, SEASON, round_num, event_name)

    con.close()
    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
