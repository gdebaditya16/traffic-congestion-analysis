
import json
import math
import pandas as pd

INPUT = "data/train.csv"
OUTPUT = "data/clean_segments.csv"

NROWS = 10000
INTERVAL_SECONDS = 15
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

df = pd.read_csv(INPUT, nrows=NROWS)
records = []
total_segments = 0
rejected_segments = 0

for _, row in df.iterrows():
    if str(row["MISSING_DATA"]).lower() == "true":
        continue

    try:
        points = json.loads(row["POLYLINE"])
        start_time = pd.to_datetime(
            row["TIMESTAMP"], unit="s", utc=True
        )
    except (ValueError, TypeError):
        continue

    for i in range(1, len(points)):
        total_segments += 1

        try:
            lon1, lat1 = points[i - 1]
            lon2, lat2 = points[i]

            # Restrict analysis to the Porto study area
            if not (
                -9.0 <= lon1 <= -8.3
                and 40.8 <= lat1 <= 41.4
                and -9.0 <= lon2 <= -8.3
                and 40.8 <= lat2 <= 41.4
            ):
                rejected_segments += 1
                continue

            distance = haversine_km(
                lon1, lat1, lon2, lat2
            )
            speed = distance / (INTERVAL_SECONDS / 3600)

            # Reject implausible GPS jumps
            if speed > MAX_SPEED_KMH:
                rejected_segments += 1
                continue

            # Use the segment midpoint for spatial aggregation
            mid_lon = (lon1 + lon2) / 2
            mid_lat = (lat1 + lat2) / 2

            # Approximate time of the segment
            timestamp = start_time + pd.Timedelta(
                seconds=(i - 1) * INTERVAL_SECONDS
            )
            local_time = timestamp.tz_convert("Europe/Lisbon")

            records.append({
                "TRIP_ID": row["TRIP_ID"],
                "LONGITUDE": mid_lon,
                "LATITUDE": mid_lat,
                "TIMESTAMP": local_time.isoformat(),
                "HOUR": local_time.hour,
                "DISTANCE_KM": distance,
                "SPEED_KMH": speed
            })

        except (ValueError, TypeError, IndexError):
            rejected_segments += 1

out = pd.DataFrame(records)
out.to_csv(OUTPUT, index=False)

print("Source trips:", len(df))
print("Segments examined:", total_segments)
print("Segments rejected:", rejected_segments)
print("Valid segments saved:", len(out))

if not out.empty:
    print("\nSpeed summary:")
    print(out["SPEED_KMH"].describe().round(2))

print("\nSaved to:", OUTPUT)
