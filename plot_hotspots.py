
import pandas as pd
import folium

INPUT_PATH = "data/potential_slow_cells.csv"
OUTPUT_PATH = "data/potential_hotspots_map.html"

df = pd.read_csv(INPUT_PATH)

m = folium.Map(
    location=[41.1579, -8.6291],
    zoom_start=11,
    tiles=None
)

for _, row in df.iterrows():
    # Approximate center of each 0.005-degree grid cell
    lat = row["GRID_LAT"] + 0.0025
    lon = row["GRID_LON"] + 0.0025
    speed = row["MEAN_SPEED_KMH"]

    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        color="red" if speed < 10 else "orange",
        fill=True,
        fill_opacity=0.8,
        tooltip=(
            f"Mean speed: {speed:.2f} km/h | "
            f"Hours observed: {int(row['HOURS_OBSERVED'])} | "
            f"Observations: {int(row['TOTAL_OBSERVATIONS'])}"
        )
    ).add_to(m)

m.save(OUTPUT_PATH)

print("Candidate hotspots:", len(df))
print("Saved to:", OUTPUT_PATH)
