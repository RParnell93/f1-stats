# F1 Stats

Interactive F1 data analytics dashboard. Race strategy, qualifying breakdowns, championship progression, and lap-by-lap analysis.

## Live App

**[f1-stats.streamlit.app](https://f1-stats.streamlit.app/)**

## Features

- **Race Analysis** - tire strategy timeline, position changes, lap time distribution
- **Qualifying** - sector-by-sector gap waterfall charts
- **Season Overview** - championship standings progression

## Data

- **Source:** [FastF1](https://github.com/theOehrly/Fast-F1) (official F1 timing data)
- **Storage:** MotherDuck (cloud DuckDB)
- **Refresh:** GitHub Actions after every session (Fri/Sat/Sun)

## Stack

- Python, Streamlit, Plotly
- FastF1 for data ingestion
- DuckDB / MotherDuck for storage
- GitHub Actions for automation

## Local Development

```bash
pip install -r requirements.txt
pip install fastf1  # for pipeline only
python snapshot.py  # load data into MotherDuck
streamlit run app.py
```

Requires `MOTHERDUCK_TOKEN` in `.env` or Streamlit secrets.
