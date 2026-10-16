
import pandas as pd
import json
import math
from collections import defaultdict

DATA_PATH = "data/train.csv"
OUTPUT_PATH = "data/grid_hourly_speeds.csv"

ROWS_TO_READ = 10000
INTERVAL_SECONDS = 15
GRID_SIZE = 0.005
MAX_SPEED_KMH = 120

def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0
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
    return 2 * r * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )

df = pd.read_csv(DATA_PATH, nrows=ROWS_TO_READ)

# Key: grid cell and hour
stats = defaultdict(lambda: {"speed_sum": 0.0, "count": 0})

for _, row in df.iterrows():
    if str(row["MISSING_DATA"]).lower() == "true":
        continue

    try:
        points = json.loads(row["POLYLINE"])
        start_time = pd.Timestamp(
            row["TIMESTAMP"], unit="s", tz="UTC"
        ).tz_convert("Europe/Lisbon")
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

            speed = haversine_km(
                lon1, lat1, lon2, lat2
            ) / (INTERVAL_SECONDS / 3600)

            if speed > MAX_SPEED_KMH:
                continue

            mid_lon = (lon1 + lon2) / 2
            mid_lat = (lat1 + lat2) / 2

            grid_x = math.floor(mid_lon / GRID_SIZE)
            grid_y = math.floor(mid_lat / GRID_SIZE)

            # Approximate timestamp for this segment
            segment_time = start_time + pd.Timedelta(
                seconds=(i - 1) * INTERVAL_SECONDS
            )
            hour = segment_time.hour

            key = (grid_x, grid_y, hour)
            stats[key]["speed_sum"] += speed
            stats[key]["count"] += 1

        except (TypeError, ValueError, IndexError):
            continue

results = []

for (grid_x, grid_y, hour), values in stats.items():
    count = values["count"]
    results.append({
        "GRID_LON": grid_x * GRID_SIZE,
        "GRID_LAT": grid_y * GRID_SIZE,
        "HOUR": hour,
        "OBSERVATIONS": count,
        "AVG_SPEED_KMH": round(
            values["speed_sum"] / count, 2
        )
    })

out = pd.DataFrame(results)
out.to_csv(OUTPUT_PATH, index=False)

print("Grid-hour records:", len(out))
print("\nSlowest grid-hour records with at least 30 observations:")
print(
    out[out["OBSERVATIONS"] >= 30]
    .sort_values("AVG_SPEED_KMH")
    .head(20)
    .to_string(index=False)
)

print("\nSaved to:", OUTPUT_PATH)
