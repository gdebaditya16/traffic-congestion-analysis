
import pandas as pd

hourly = pd.read_csv("data/grid_hourly_speeds.csv")
hotspots = pd.read_csv("data/potential_slow_cells.csv")

merged = hourly.merge(
    hotspots[["GRID_LON", "GRID_LAT"]],
    on=["GRID_LON", "GRID_LAT"],
    how="inner"
)

# Ignore weak grid-hour samples
merged = merged[merged["OBSERVATIONS"] >= 100]

slowest_hours = (
    merged.sort_values("AVG_SPEED_KMH")
    .groupby(["GRID_LON", "GRID_LAT"])
    .head(1)
    .sort_values("AVG_SPEED_KMH")
)

print("Slowest observed hour for each candidate hotspot:")
print(
    slowest_hours[
        [
            "GRID_LON",
            "GRID_LAT",
            "HOUR",
            "OBSERVATIONS",
            "AVG_SPEED_KMH"
        ]
    ].to_string(index=False)
)

slowest_hours.to_csv(
    "data/hotspot_slowest_hours.csv",
    index=False
)

print("\nSaved to data/hotspot_slowest_hours.csv")