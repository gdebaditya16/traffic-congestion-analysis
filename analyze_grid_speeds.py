
import pandas as pd
import json
import math
from collections import defaultdict

DATA_PATH = "data/train.csv"
OUTPUT_PATH = "data/grid_speed_analysis.csv"

ROWS_TO_READ = 10000
INTERVAL_SECONDS = 15
GRID_SIZE_DEGREES = 0.005
MAX_SPEED_KMH = 120

def haversine_km(lon1, lat1, lon2, lat2):
    radius = 6371.0

    lon1, lat1, lon2, lat2 = map(
        math.radians, [lon1, lat1, lon2, lat2]
    )

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )

df = pd.read_csv(DATA_PATH, nrows=ROWS_TO_READ)

grid_stats = defaultdict(lambda: {
    "speed_sum": 0.0,
    "observations": 0
})

for _, row in df.iterrows():
    if str(row["MISSING_DATA"]).lower() == "true":
        continue

    try:
        points = json.loads(row["POLYLINE"])
    except (ValueError, TypeError):
        continue

    for i in range(1, len(points)):
        try:
            lon1, lat1 = points[i - 1]
            lon2, lat2 = points[i]

            if not (
                -9.0 <= lon1 <= -8.3
                and 40.8 <= lat1 <= 41.4
                and -9.0 <= lon2 <= -8.3
                and 40.8 <= lat2 <= 41.4
            ):
                continue

            distance = haversine_km(
                lon1, lat1, lon2, lat2
            )

            speed = distance / (INTERVAL_SECONDS / 3600)

            if speed > MAX_SPEED_KMH:
                continue

            # Assign each segment to the midpoint's grid cell
            mid_lon = (lon1 + lon2) / 2
            mid_lat = (lat1 + lat2) / 2

            grid_x = math.floor(mid_lon / GRID_SIZE_DEGREES)
            grid_y = math.floor(mid_lat / GRID_SIZE_DEGREES)

            key = (grid_x, grid_y)

            grid_stats[key]["speed_sum"] += speed
            grid_stats[key]["observations"] += 1

        except (TypeError, ValueError, IndexError):
            continue

results = []

for (grid_x, grid_y), stats in grid_stats.items():
    count = stats["observations"]

    results.append({
        "GRID_LON": grid_x * GRID_SIZE_DEGREES,
        "GRID_LAT": grid_y * GRID_SIZE_DEGREES,
        "OBSERVATIONS": count,
        "AVG_SPEED_KMH": round(
            stats["speed_sum"] / count, 2
        )
    })

out = pd.DataFrame(results)

if not out.empty:
    out = out.sort_values("OBSERVATIONS", ascending=False)

out.to_csv(OUTPUT_PATH, index=False)

print("Grid cells analyzed:", len(out))
print("Valid segment observations:", sum(
    stats["observations"] for stats in grid_stats.values()
))
print("\nTop 15 grid cells by observation count:")
print(out.head(15).to_string(index=False))
print("\nSaved to:", OUTPUT_PATH)