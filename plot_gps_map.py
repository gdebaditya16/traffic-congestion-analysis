
import pandas as pd
import json
import folium

df = pd.read_csv("data/train.csv", nrows=10000)

points = []

for _, row in df.iterrows():
    try:
        trajectory = json.loads(row["POLYLINE"])
    except (ValueError, TypeError):
        continue

    # Sample points to keep the map lightweight
    for lon, lat in trajectory[::10]:
        if -9.0 <= lon <= -8.3 and 40.8 <= lat <= 41.4:
            points.append((lat, lon))

print("GPS points selected for map:", len(points))

# Center map around Porto
m = folium.Map(
    location=[41.1579, -8.6291],
    zoom_start=12,
    tiles=None
)

# Plot a limited sample of points
for lat, lon in points[:3000]:
    folium.CircleMarker(
        location=[lat, lon],
        radius=2,
        color="blue",
        fill=True,
        fill_opacity=0.4,
        weight=0
    ).add_to(m)

m.save("data/gps_points_map.html")

print("Map saved to data/gps_points_map.html")