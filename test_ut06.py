
import pandas as pd

# Sample GPS segment observations belonging to the same grid cell
data = pd.DataFrame({
    "GRID_LON": [-8.61, -8.61, -8.61, -8.61],
    "GRID_LAT": [41.15, 41.15, 41.15, 41.15],
    "SPEED_KMH": [10.0, 20.0, 30.0, 40.0]
})

# Aggregate observations by grid cell
result = data.groupby(
    ["GRID_LON", "GRID_LAT"]
).agg(
    OBSERVATIONS=("SPEED_KMH", "count"),
    AVG_SPEED_KMH=("SPEED_KMH", "mean"),
    MEDIAN_SPEED_KMH=("SPEED_KMH", "median")
).reset_index()

row = result.iloc[0]

print("Grid cells:", len(result))
print("Observation count:", row["OBSERVATIONS"])
print("Average speed:", row["AVG_SPEED_KMH"])
print("Median speed:", row["MEDIAN_SPEED_KMH"])

assert len(result) == 1
assert row["OBSERVATIONS"] == 4
assert row["AVG_SPEED_KMH"] == 25.0
assert row["MEDIAN_SPEED_KMH"] == 25.0

print("UT-06 PASSED")
