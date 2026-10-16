
import pandas as pd
import json

df = pd.read_csv("data/train.csv", nrows=10000)

print("Total rows:", len(df))
print("\nMissing-data flags:")
print(df["MISSING_DATA"].value_counts(dropna=False))

coordinates = []

for _, row in df.iterrows():
    try:
        points = json.loads(row["POLYLINE"])

        for point in points:
            if len(point) != 2:
                continue

            lon, lat = point

            if (
                -180 <= lon <= 180
                and -90 <= lat <= 90
            ):
                coordinates.append((lon, lat))

    except (ValueError, TypeError):
        continue

coords = pd.DataFrame(coordinates, columns=["LONGITUDE", "LATITUDE"])

print("\nValid GPS points:", len(coords))

if not coords.empty:
    print("\nCoordinate ranges:")
    print(coords.agg(["min", "max"]))

    print("\nFirst 10 coordinates:")
    print(coords.head(10).to_string(index=False))