
import math
import pandas as pd
import streamlit as st
import pydeck as pdk

DATA_PATH = "data/clean_segments.csv"
GRID_SIZE = 0.005

# Fixed speed scale for consistent comparison across hours.
MIN_SPEED_SCALE = 0.0
MAX_SPEED_SCALE = 60.0

st.set_page_config(
    page_title="Traffic Congestion Analysis",
    page_icon="🚦",
    layout="wide"
)

st.title("Traffic Congestion Analysis Using GPS Data")
st.caption(
    "Exploratory analysis of taxi GPS trajectories from Porto, Portugal"
)


# -------------------- LOAD DATA --------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "TIMESTAMP", "LONGITUDE", "LATITUDE", "SPEED_KMH"
    ]

    missing = [
        col for col in required_columns if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns in {DATA_PATH}: {missing}"
        )

    df["TIMESTAMP"] = pd.to_datetime(
        df["TIMESTAMP"], utc=True, errors="coerce"
    )

    for col in ["LONGITUDE", "LATITUDE", "SPEED_KMH"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(
        subset=[
            "TIMESTAMP", "LONGITUDE", "LATITUDE", "SPEED_KMH"
        ]
    ).copy()

    df = df[
        df["LONGITUDE"].between(-180, 180)
        & df["LATITUDE"].between(-90, 90)
        & df["SPEED_KMH"].between(0, 120)
    ].copy()

    # Convert timestamps to local Porto time.
    df["HOUR"] = (
        df["TIMESTAMP"]
        .dt.tz_convert("Europe/Lisbon")
        .dt.hour
    )

    # Assign each observation to a geographic grid cell.
    df["GRID_LON"] = (
        df["LONGITUDE"].apply(
            lambda x: math.floor(x / GRID_SIZE)
        ) * GRID_SIZE
    )

    df["GRID_LAT"] = (
        df["LATITUDE"].apply(
            lambda x: math.floor(x / GRID_SIZE)
        ) * GRID_SIZE
    )

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the GPS data: {e}")
    st.stop()


# -------------------- SIDEBAR FILTERS --------------------

st.sidebar.header("Dashboard filters")

selected_hour = st.sidebar.selectbox(
    "Select hour in Porto",
    ["All hours"] + list(range(24))
)

min_observations = st.sidebar.slider(
    "Minimum observations per grid cell",
    min_value=10,
    max_value=500,
    value=100,
    step=10
)

filtered = df.copy()

if selected_hour != "All hours":
    filtered = filtered[
        filtered["HOUR"] == selected_hour
    ].copy()


# -------------------- SUMMARY METRICS --------------------

st.subheader("Summary")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Valid GPS segments",
    f"{len(filtered):,}"
)

col2.metric(
    "Mean segment speed",
    (
        f"{filtered['SPEED_KMH'].mean():.2f} km/h"
        if not filtered.empty else "N/A"
    )
)

col3.metric(
    "Median segment speed",
    (
        f"{filtered['SPEED_KMH'].median():.2f} km/h"
        if not filtered.empty else "N/A"
    )
)


# -------------------- SPEED DISTRIBUTION --------------------

st.subheader("Segment speed distribution")

if not filtered.empty:
    bins = list(range(0, 126, 5))

    labels = [
        f"{bins[i]}–{bins[i + 1]}"
        for i in range(len(bins) - 1)
    ]

    speed_bins = pd.cut(
        filtered["SPEED_KMH"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    histogram = (
        speed_bins.value_counts(sort=False)
        .rename_axis("Speed range (km/h)")
        .reset_index(name="Number of segments")
    )

    st.bar_chart(
        histogram,
        x="Speed range (km/h)",
        y="Number of segments"
    )
else:
    st.info("No segments for this hour selection.")


# -------------------- HOURLY SPEED ANALYSIS --------------------

st.subheader("Hourly speed analysis")

hourly = (
    df.groupby("HOUR")["SPEED_KMH"]
    .agg(
        mean_speed="mean",
        median_speed="median",
        segments="count"
    )
    .reindex(range(24))
    .reset_index()
)

hourly.columns = [
    "Hour",
    "Mean speed (km/h)",
    "Median speed (km/h)",
    "Segments"
]

st.line_chart(
    hourly.set_index("Hour")[
        ["Mean speed (km/h)", "Median speed (km/h)"]
    ]
)

st.caption(
    "This chart uses all available data, independently of the "
    "selected-hour filter. Lower average speed can indicate a "
    "slowdown, but does not by itself confirm congestion."
)

with st.expander("View hourly statistics"):
    st.dataframe(
        hourly.round(2),
        use_container_width=True,
        hide_index=True
    )


# -------------------- GRID CELL ANALYSIS --------------------

st.subheader("Candidate slow grid cells")

grid = pd.DataFrame(
    columns=[
        "GRID_LON",
        "GRID_LAT",
        "OBSERVATIONS",
        "AVG_SPEED_KMH",
        "MEDIAN_SPEED_KMH"
    ]
)

if filtered.empty:
    st.info("No data available for the selected hour.")
else:
    grid = (
        filtered.groupby(["GRID_LON", "GRID_LAT"])
        .agg(
            OBSERVATIONS=("SPEED_KMH", "size"),
            AVG_SPEED_KMH=("SPEED_KMH", "mean"),
            MEDIAN_SPEED_KMH=("SPEED_KMH", "median")
        )
        .reset_index()
    )

    grid = grid[
        grid["OBSERVATIONS"] >= min_observations
    ].copy()

    grid = grid.sort_values("AVG_SPEED_KMH")

    if grid.empty:
        st.warning(
            "No grid cells meet the observation threshold. "
            "Lower the minimum observations slider or select All hours."
        )
    else:
        st.caption(
            "Grid cells are ordered by average speed, lowest first."
        )

        display_grid = grid.rename(
            columns={
                "GRID_LON": "Grid longitude",
                "GRID_LAT": "Grid latitude",
                "OBSERVATIONS": "Observations",
                "AVG_SPEED_KMH": "Average speed (km/h)",
                "MEDIAN_SPEED_KMH": "Median speed (km/h)"
            }
        )

        st.dataframe(
            display_grid.round(2),
            use_container_width=True,
            hide_index=True
        )


# -------------------- GEOGRAPHIC DISTRIBUTION --------------------

st.subheader("Geographic distribution")

if selected_hour == "All hours":
    st.caption("Map shows grid-cell speeds across all hours.")
else:
    next_hour = (selected_hour + 1) % 24
    st.caption(
        f"Map shows grid-cell speeds from {selected_hour:02d}:00 "
        f"to {next_hour:02d}:00 Porto local time."
    )

if grid.empty:
    st.warning(
        "No grid cells are available for mapping. "
        "Try selecting All hours or lowering the observation threshold."
    )
else:
    map_data = grid[
        [
            "GRID_LON",
            "GRID_LAT",
            "OBSERVATIONS",
            "AVG_SPEED_KMH",
            "MEDIAN_SPEED_KMH"
        ]
    ].copy()

    map_data = map_data.rename(
        columns={
            "GRID_LON": "longitude",
            "GRID_LAT": "latitude"
        }
    )

    map_data = map_data.dropna(
        subset=["longitude", "latitude", "AVG_SPEED_KMH"]
    )

    # Restrict map points to the Porto study region.
    map_data = map_data[
        map_data["longitude"].between(-9.2, -7.5)
        & map_data["latitude"].between(40.5, 42.5)
    ].copy()

    st.write(f"Grid cells before mapping: {len(grid)}")
    st.write(f"Valid map points: {len(map_data)}")

    if map_data.empty:
        st.error("No valid coordinates were found for the map.")
    else:
        # Fixed color scale: 0 km/h = red, 30 = yellow, 60+ = green.
        normalized_speed = (
            (map_data["AVG_SPEED_KMH"] - MIN_SPEED_SCALE)
            / (MAX_SPEED_SCALE - MIN_SPEED_SCALE)
        ).clip(0, 1)

        def speed_to_color(value):
            if value <= 0.5:
                # Red to yellow.
                t = value * 2
                return [
                    220,
                    int(40 + 160 * t),
                    40,
                    210
                ]

            # Yellow to green.
            t = (value - 0.5) * 2
            return [
                int(220 * (1 - t) + 30 * t),
                int(200 * (1 - t) + 190 * t),
                40,
                210
            ]

        map_data["fill_color"] = normalized_speed.apply(
            speed_to_color
        )

        map_data["radius"] = 65

        # -------------------- SPEED LEGEND --------------------

        st.markdown("**Average speed legend**")

        legend_col1, legend_col2, legend_col3 = st.columns(
            [1, 3, 1]
        )

        with legend_col1:
            st.markdown("🔴 **0 km/h**")

        with legend_col2:
            st.markdown(
                """
                <div style="
                    height: 14px;
                    width: 100%;
                    border-radius: 7px;
                    background: linear-gradient(
                        to right,
                        #dc2828,
                        #dca028,
                        #1ebe28
                    );
                    margin-top: 5px;
                "></div>
                """,
                unsafe_allow_html=True
            )

        with legend_col3:
            st.markdown("🟢 **60+ km/h**")

        st.caption(
            "Red represents lower speeds, yellow represents around "
            "30 km/h, and green represents 60 km/h or higher. "
            "The scale remains fixed when changing hours."
        )

        # -------------------- PYDECK MAP --------------------

        view_state = pdk.ViewState(
            latitude=41.1579,
            longitude=-8.6291,
            zoom=10,
            pitch=0
        )

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position="[longitude, latitude]",
            get_radius="radius",
            get_fill_color="fill_color",
            radius_min_pixels=4,
            radius_max_pixels=16,
            pickable=True,
            auto_highlight=True
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style=None,
            tooltip={
                "html": (
                    "<b>Average speed:</b> "
                    "{AVG_SPEED_KMH} km/h<br/>"
                    "<b>Median speed:</b> "
                    "{MEDIAN_SPEED_KMH} km/h<br/>"
                    "<b>Observations:</b> "
                    "{OBSERVATIONS}"
                ),
                "style": {
                    "backgroundColor": "#222222",
                    "color": "white"
                }
            }
        )

        st.pydeck_chart(
            deck,
            use_container_width=True
        )

        with st.expander("View mapped grid data"):
            st.dataframe(
                map_data[
                    [
                        "longitude",
                        "latitude",
                        "OBSERVATIONS",
                        "AVG_SPEED_KMH",
                        "MEDIAN_SPEED_KMH"
                    ]
                ].round(4),
                use_container_width=True,
                hide_index=True
            )


# -------------------- METHODOLOGY NOTE --------------------

st.divider()

st.info(
    "Methodology: Segment speeds are estimated from GPS point "
    "spacing and an assumed 15-second sampling interval. Results "
    "may be affected by GPS noise, stationary vehicles, route "
    "differences, and sampling bias. Low speed is a candidate "
    "indicator only; it does not independently establish congestion."
)

