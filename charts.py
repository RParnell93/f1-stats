"""Reusable Plotly chart functions for F1 data."""

import plotly.graph_objects as go
import pandas as pd
from style import apply_template, get_team_color, get_compound_color, POSITIVE, NEGATIVE


def strategy_timeline(laps_df, results_df, title="Race Strategy"):
    """Tire strategy Gantt chart - the signature visualization.

    Args:
        laps_df: Laps DataFrame with compound, tyre_life, driver, lap_number
        results_df: Results DataFrame with position, driver, team
    """
    # Build stint data from laps
    drivers = results_df.sort_values("position")["driver"].tolist()
    teams = dict(zip(results_df["driver"], results_df["team"]))

    fig = go.Figure()

    for i, driver in enumerate(drivers):
        driver_laps = laps_df[laps_df["driver"] == driver].sort_values("lap_number")
        if driver_laps.empty:
            continue

        # Detect stint boundaries (compound changes or tyre_life resets)
        stints = []
        stint_start = driver_laps.iloc[0]["lap_number"]
        stint_compound = driver_laps.iloc[0]["compound"]

        for _, lap in driver_laps.iterrows():
            if lap["compound"] != stint_compound or lap.get("pit_out", False):
                stints.append((stint_start, lap["lap_number"] - 1, stint_compound))
                stint_start = lap["lap_number"]
                stint_compound = lap["compound"]
        # Final stint
        stints.append((stint_start, driver_laps.iloc[-1]["lap_number"], stint_compound))

        y_pos = len(drivers) - i  # P1 at top

        for start, end, compound in stints:
            color = get_compound_color(compound or "UNKNOWN")
            fig.add_trace(go.Bar(
                x=[end - start + 1],
                y=[y_pos],
                base=start - 1,
                orientation="h",
                marker=dict(color=color, line=dict(color="#333", width=0.5)),
                name=compound if compound else "Unknown",
                showlegend=False,
                hovertemplate=(
                    f"<b>{driver}</b><br>"
                    f"Compound: {compound}<br>"
                    f"Laps {start}-{end} ({end - start + 1} laps)"
                    "<extra></extra>"
                ),
            ))

    # Y-axis labels: driver abbreviation + position
    fig.update_layout(
        title=title,
        xaxis_title="Lap",
        yaxis=dict(
            tickmode="array",
            tickvals=list(range(1, len(drivers) + 1)),
            ticktext=[f"P{len(drivers) - i} {d}" for i, d in enumerate(drivers)],
        ),
        barmode="stack",
        height=max(400, len(drivers) * 28),
    )

    # Add compound legend manually
    for compound in ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]:
        fig.add_trace(go.Bar(
            x=[0], y=[0], marker=dict(color=get_compound_color(compound)),
            name=compound.capitalize(), showlegend=True, visible="legendonly",
        ))

    return apply_template(fig)


def position_changes(laps_df, results_df, title="Position Changes"):
    """Lap-by-lap position spaghetti chart."""
    fig = go.Figure()

    teams = dict(zip(results_df["driver"], results_df["team"]))
    drivers = results_df.sort_values("position")["driver"].tolist()

    for driver in drivers:
        driver_laps = laps_df[
            (laps_df["driver"] == driver) & (laps_df["lap_number"] > 0)
        ].sort_values("lap_number")

        if driver_laps.empty or "position" not in driver_laps.columns:
            continue

        # Filter out NaN positions
        valid = driver_laps.dropna(subset=["position"])
        if valid.empty:
            continue

        team = teams.get(driver, "Unknown")
        color = get_team_color(team)

        fig.add_trace(go.Scatter(
            x=valid["lap_number"],
            y=valid["position"],
            mode="lines",
            name=driver,
            line=dict(color=color, width=2),
            hovertemplate=f"<b>{driver}</b><br>Lap %{{x}}<br>P%{{y}}<extra></extra>",
        ))

    max_pos = min(20, int(laps_df["position"].max()) if "position" in laps_df.columns and laps_df["position"].notna().any() else 20)

    fig.update_layout(
        title=title,
        xaxis_title="Lap",
        yaxis=dict(title="Position", autorange="reversed", dtick=1, range=[0.5, max_pos + 0.5]),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.3),
    )

    return apply_template(fig)


def lap_time_distribution(laps_df, results_df, title="Lap Time Distribution"):
    """Violin/box plot of lap times per driver."""
    fig = go.Figure()

    teams = dict(zip(results_df["driver"], results_df["team"]))
    drivers = results_df.sort_values("position")["driver"].tolist()

    for driver in drivers[:10]:  # Top 10 only
        driver_laps = laps_df[
            (laps_df["driver"] == driver)
            & (laps_df["lap_time_ms"].notna())
            & (laps_df["lap_time_ms"] > 0)
            & (~laps_df["pit_in"].fillna(False))
            & (~laps_df["pit_out"].fillna(False))
        ]

        # Filter out SC laps (track_status != '1' if available)
        if "track_status" in driver_laps.columns:
            driver_laps = driver_laps[driver_laps["track_status"].isin(["1", "1 ", None, ""])]

        if driver_laps.empty:
            continue

        lap_times_sec = driver_laps["lap_time_ms"] / 1000.0
        team = teams.get(driver, "Unknown")
        color = get_team_color(team)

        fig.add_trace(go.Violin(
            y=lap_times_sec,
            name=driver,
            marker=dict(color=color),
            box_visible=True,
            meanline_visible=True,
            line=dict(color=color),
        ))

    fig.update_layout(
        title=title,
        yaxis_title="Lap Time (s)",
        showlegend=False,
        height=500,
    )

    return apply_template(fig)


def qualifying_waterfall(laps_df, results_df, title="Qualifying - Sector Gaps to Pole"):
    """Waterfall chart showing sector-by-sector gaps relative to P1."""
    if results_df.empty:
        return go.Figure()

    # Get best lap per driver from qualifying
    best_laps = laps_df[
        laps_df["lap_time_ms"].notna() & (laps_df["lap_time_ms"] > 0)
    ].loc[laps_df.groupby("driver")["lap_time_ms"].idxmin()]

    if best_laps.empty:
        return go.Figure()

    best_laps = best_laps.sort_values("lap_time_ms")
    pole_driver = best_laps.iloc[0]

    fig = go.Figure()
    drivers_to_show = best_laps.head(10)

    for _, row in drivers_to_show.iterrows():
        if row["driver"] == pole_driver["driver"]:
            continue

        s1_delta = (row["sector1_ms"] - pole_driver["sector1_ms"]) / 1000 if pd.notna(row["sector1_ms"]) and pd.notna(pole_driver["sector1_ms"]) else 0
        s2_delta = (row["sector2_ms"] - pole_driver["sector2_ms"]) / 1000 if pd.notna(row["sector2_ms"]) and pd.notna(pole_driver["sector2_ms"]) else 0
        s3_delta = (row["sector3_ms"] - pole_driver["sector3_ms"]) / 1000 if pd.notna(row["sector3_ms"]) and pd.notna(pole_driver["sector3_ms"]) else 0

        team = results_df[results_df["driver"] == row["driver"]]["team"].iloc[0] if not results_df[results_df["driver"] == row["driver"]].empty else "Unknown"

        fig.add_trace(go.Waterfall(
            name=row["driver"],
            orientation="v",
            x=[f"{row['driver']}<br>S1", f"{row['driver']}<br>S2", f"{row['driver']}<br>S3", f"{row['driver']}<br>Total"],
            measure=["relative", "relative", "relative", "total"],
            y=[s1_delta, s2_delta, s3_delta, 0],
            increasing=dict(marker=dict(color=NEGATIVE)),
            decreasing=dict(marker=dict(color=POSITIVE)),
            totals=dict(marker=dict(color=get_team_color(team))),
            showlegend=False,
            hovertemplate="%{x}: %{y:+.3f}s<extra></extra>",
        ))

    fig.update_layout(
        title=f"{title} (vs {pole_driver['driver']})",
        yaxis_title="Gap to Pole (s)",
        height=450,
        showlegend=False,
    )

    return apply_template(fig)


def championship_progression(standings_df, title="Championship Standings"):
    """Line chart of cumulative points by round."""
    fig = go.Figure()

    if standings_df.empty:
        return apply_template(fig)

    # Get latest standings to determine order
    latest_round = standings_df["round"].max()
    latest = standings_df[standings_df["round"] == latest_round].sort_values("position")

    for _, row in latest.iterrows():
        driver = row["driver"]
        team = row["team"]
        driver_data = standings_df[standings_df["driver"] == driver].sort_values("round")
        color = get_team_color(team)

        fig.add_trace(go.Scatter(
            x=driver_data["round"],
            y=driver_data["points"],
            mode="lines+markers",
            name=driver,
            line=dict(color=color, width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>{driver}</b><br>Round %{{x}}<br>%{{y}} pts<extra></extra>",
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Round",
        yaxis_title="Points",
        height=500,
    )

    return apply_template(fig)
