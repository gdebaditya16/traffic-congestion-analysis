
import pandas as pd
import json
import math

DATA_PATH = "data/train.csv"
INTERVAL_SECONDS = 15
JUMP_SPEED_KMH = 120

def haversine_km(lon1, lat1, lon2, lat2):
    radius = 6371.0

    lon1, lat1, lon2, lat2 = map(
        math.radians, [lon1, lat1, lon2, lat2]
    )

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    return radius * 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )

df = pd.read_csv(DATA_PATH, nrows=100)

for _, row in df.iterrows():
    if row["MISSING_DATA"]:
        continue

    try:
        points = json.loads(row["POLYLINE"])
    except (ValueError, TypeError):
        continue

    if len(points) < 2:
        continue

    suspicious = []

    for i in range(1, len(points)):
        lon1, lat1 = points[i - 1]
        lon2, lat2 = points[i]

        distance = haversine_km(lon1, lat1, lon2, lat2)
        speed = distance / (INTERVAL_SECONDS / 3600)

        if speed > JUMP_SPEED_KMH:
            suspicious.append({
                "point": i,
                "distance_km": round(distance, 3),
                "speed_kmh": round(speed, 1)
            })

    if suspicious:
        print(f"\nTrip ID: {row['TRIP_ID']}")
        print("Suspicious GPS jumps:")
        for item in suspicious:
            print(item)

print("\nGPS jump check completed.")