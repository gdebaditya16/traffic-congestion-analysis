
import pandas as pd

INPUT_PATH = "data/grid_hourly_speeds.csv"

df = pd.read_csv(INPUT_PATH)

# Require enough observations for a more stable estimate
df = df[df["OBSERVATIONS"] >= 100].copy()

print("Grid-hour records with at least 100 observations:", len(df))

# Rank slow grid-hour combinations
print("\nSlowest grid-hour combinations:")
print(
    df.sort_values("AVG_SPEED_KMH")
      .head(20)
      .to_string(index=False)
)

# Identify cells that repeatedly appear across hours
cell_summary = (
    df.groupby(["GRID_LON", "GRID_LAT"])
      .agg(
          HOURS_OBSERVED=("HOUR", "nunique"),
          TOTAL_OBSERVATIONS=("OBSERVATIONS", "sum"),
          MEAN_SPEED_KMH=("AVG_SPEED_KMH", "mean"),
          MEDIAN_OF_HOURLY_SPEEDS=("AVG_SPEED_KMH", "median")
      )
      .reset_index()
)

# Exploratory threshold; not a universal congestion definition
repeated_slow = cell_summary[
    (cell_summary["HOURS_OBSERVED"] >= 3)
    & (cell_summary["MEAN_SPEED_KMH"] < 15)
].sort_values("MEAN_SPEED_KMH")

print("\nPotential repeatedly slow grid cells:")
print("Number of cells:", len(repeated_slow))
print(repeated_slow.head(20).to_string(index=False))

cell_summary.to_csv("data/grid_hotspot_summary.csv", index=False)
repeated_slow.to_csv("data/potential_slow_cells.csv", index=False)

print("\nSaved:")
print("data/grid_hotspot_summary.csv")
print("data/potential_slow_cells.csv")