# F1 Stats - Project Instructions

## Overview
F1 data analytics dashboard. Streamlit app reads from MotherDuck. FastF1 pipeline runs separately (locally or via GitHub Actions).

## Architecture
- **App** (app.py + pages/): Streamlit, reads from MotherDuck only. No FastF1 imports.
- **Pipeline** (snapshot.py): FastF1 -> MotherDuck. Runs locally or in GitHub Actions.
- **Charts** (charts.py): Reusable Plotly chart functions.
- **Style** (style.py): F1 dark theme template, CSS, color helpers.
- **Config** (config.py): Team colors, compound colors, constants.
- **DB** (db.py): MotherDuck connection + cached query helpers.

## Key Rules
- Never import fastf1 in the Streamlit app (app.py or pages/). It's too slow and heavy.
- DuckDB pinned to v1.4.4 for MotherDuck compatibility.
- kaleido 0.2.1 for Plotly PNG export (local only, not in requirements.txt).
- Always use `config={"displayModeBar": False, "scrollZoom": False}` for Plotly in Streamlit.
- Team colors from config.py TEAM_COLORS dict. Compound colors from COMPOUND_COLORS dict.
- MotherDuck database name: f1_stats

## Data
- Laps, results, pit stops, standings stored in MotherDuck (~7MB/season).
- Full telemetry NOT stored (30-50GB/season). Use FastF1 local cache for telemetry work.
- Pipeline is idempotent - skip sessions already loaded.

## Testing
- `streamlit run app.py` to test the app locally
- `python snapshot.py` to test the pipeline
