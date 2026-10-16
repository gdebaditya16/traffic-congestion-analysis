

import json
import math
import pandas as pd

INPUT_FILE = "data/train.csv"
OUTPUT_FILE = "data/trip_analysis.csv"

EARTH_RADIUS_KM = 6371
INTERVAL_SECONDS = 15


def distance_km(p1, p2):
    lon1, lat1 = map(math.radians, p1)
    lon2, lat2 = map(math.radians, p2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * EARTH_RADIUS_KM * math.asin(
        math.sqrt(min(1, a))
    )


df = pd.read_csv(INPUT_FILE, nrows=100)
results = []

for _, row in df.iterrows():
    if row["MISSING_DATA"]:
        continue

    try:
        points = json.loads(row["POLYLINE"])
    except (TypeError, json.JSONDecodeError):
        continue

    if len(points) < 2:
        continue

    # Validate coordinates: [longitude, latitude]
    valid = all(
        isinstance(p, list)
        and len(p) == 2
        and all(isinstance(v, (int, float)) for v in p)
        and -180 <= p[0] <= 180
        and -90 <= p[1] <= 90
        for p in points
    )

    if not valid:
        continue

    total_distance = sum(
        distance_km(points[i], points[i + 1])
        for i in range(len(points) - 1)
    )

    duration_seconds = (len(points) - 1) * INTERVAL_SECONDS
    duration_minutes = duration_seconds / 60
    speed_kmh = total_distance / (duration_seconds / 3600)

    results.append({
        "TRIP_ID": row["TRIP_ID"],
        "GPS_POINTS": len(points),
        "DISTANCE_KM": round(total_distance, 3),
        "DURATION_MIN": round(duration_minutes, 2),
        "AVG_SPEED_KMH": round(speed_kmh, 2),
    })

result_df = pd.DataFrame(results)
result_df.to_csv(OUTPUT_FILE, index=False)

print("Trips analyzed:", len(result_df))
print("\nFirst 5 results:")
print(result_df.head())
print("\nSummary statistics:")
print(result_df[["DISTANCE_KM", "DURATION_MIN", "AVG_SPEED_KMH"]].describe())
print(f"\nSaved results to {OUTPUT_FILE}")