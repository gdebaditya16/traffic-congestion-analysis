
import pandas as pd
import folium
from folium.plugins import HeatMap

INPUT_PATH = "data/grid_speed_analysis.csv"
OUTPUT_PATH = "data/grid_speed_map.html"

df = pd.read_csv(INPUT_PATH)

# Ignore cells with too few observations
df = df[df["OBSERVATIONS"] >= 100]

# Keep the map focused on the study area
df = df[
    df["GRID_LON"].between(-9.0, -8.3)
    & df["GRID_LAT"].between(40.8, 41.4)
].copy()

print("Grid cells displayed:", len(df))

if df.empty:
    raise ValueError("No grid cells remain after filtering.")

# HeatMap intensity represents relative observation density,
# not congestion severity.
m = folium.Map(
    location=[41.1579, -8.6291],
    zoom_start=12,
    tiles=None
)

HeatMap(
    df[["GRID_LAT", "GRID_LON", "OBSERVATIONS"]].values.tolist(),
    radius=18,
    blur=15,
    min_opacity=0.3
).add_to(m)

# Add circles with exact average speed values
for _, row in df.iterrows():
    folium.CircleMarker(
        location=[row["GRID_LAT"] + 0.0025,
                  row["GRID_LON"] + 0.0025],
        radius=4,
        color="red" if row["AVG_SPEED_KMH"] < 15 else "blue",
        fill=True,
        fill_opacity=0.7,
        tooltip=(
            f"Mean speed: {row['AVG_SPEED_KMH']:.1f} km/h | "
            f"Observations: {int(row['OBSERVATIONS'])}"
        )
    ).add_to(m)

m.save(OUTPUT_PATH)
print("Map saved to:", OUTPUT_PATH)