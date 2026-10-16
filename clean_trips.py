
import pandas as pd
import json
import math

DATA_PATH = "data/train.csv"
OUTPUT_PATH = "data/clean_trip_analysis.csv"

INTERVAL_SECONDS = 15
MAX_SEGMENT_SPEED_KMH = 120

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

df = pd.read_csv(DATA_PATH, nrows=10000)
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

    clean_distance = 0.0
    flagged_segments = 0
    valid_segments = 0

    for i in range(1, len(points)):
        try:
            lon1, lat1 = points[i - 1]
            lon2, lat2 = points[i]

            # Skip malformed or out-of-range coordinates
            if not (
                -180 <= lon1 <= 180
                and -180 <= lon2 <= 180
                and -90 <= lat1 <= 90
                and -90 <= lat2 <= 90
            ):
                flagged_segments += 1
                continue

            distance = haversine_km(
                lon1, lat1, lon2, lat2
            )

            speed = distance / (INTERVAL_SECONDS / 3600)

            if speed > MAX_SEGMENT_SPEED_KMH:
                flagged_segments += 1
                continue

            clean_distance += distance
            valid_segments += 1

        except (TypeError, ValueError):
            flagged_segments += 1

    if valid_segments == 0:
        continue

    # Keep the original observed time span.
    duration_min = (len(points) - 1) * INTERVAL_SECONDS / 60

    results.append({
        "TRIP_ID": row["TRIP_ID"],
        "VALID_SEGMENTS": valid_segments,
        "FLAGGED_SEGMENTS": flagged_segments,
        "CLEAN_DISTANCE_KM": round(clean_distance, 3),
        "DURATION_MIN": round(duration_min, 2),
        "CLEAN_AVG_SPEED_KMH": round(
            clean_distance / (duration_min / 60), 2
        )
    })

out = pd.DataFrame(results)
out.to_csv(OUTPUT_PATH, index=False)

print("Trips processed:", len(out))
print("Total flagged segments:", out["FLAGGED_SEGMENTS"].sum())
print("\nFirst 10 cleaned trips:")
print(out.head(10).to_string(index=False))
print("\nSaved to:", OUTPUT_PATH)