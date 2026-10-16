
import pandas as pd
import json
import math

DATA_PATH = "data/train.csv"
OUTPUT_PATH = "data/trip_analysis.csv"
ROWS_TO_READ = 10000
INTERVAL_SECONDS = 15

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
results = []

for _, row in df.iterrows():
    if str(row["MISSING_DATA"]).lower() == "true":
        continue

    try:
        points = json.loads(row["POLYLINE"])
    except (ValueError, TypeError):
        continue

    if not isinstance(points, list) or len(points) < 2:
        continue

    distance = 0.0
    valid = True

    try:
        for i in range(1, len(points)):
            lon1, lat1 = points[i - 1]
            lon2, lat2 = points[i]

            if not (
                -180 <= lon1 <= 180
                and -180 <= lon2 <= 180
                and -90 <= lat1 <= 90
                and -90 <= lat2 <= 90
            ):
                valid = False
                break

            distance += haversine_km(
                lon1, lat1, lon2, lat2
            )
    except (TypeError, ValueError, IndexError):
        valid = False

    if not valid:
        continue

    duration_min = (
        (len(points) - 1) * INTERVAL_SECONDS / 60
    )

    if duration_min <= 0:
        continue

    results.append({
        "TRIP_ID": row["TRIP_ID"],
        "GPS_POINTS": len(points),
        "DISTANCE_KM": round(distance, 3),
        "DURATION_MIN": round(duration_min, 2),
        "AVG_SPEED_KMH": round(
            distance / (duration_min / 60), 2
        )
    })

out = pd.DataFrame(results)
out.to_csv(OUTPUT_PATH, index=False)

print("Trips analyzed:", len(out))
print("Saved to:", OUTPUT_PATH)