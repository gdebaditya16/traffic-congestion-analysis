
import pandas as pd
import matplotlib.pyplot as plt

raw = pd.read_csv("data/trip_analysis.csv")
clean = pd.read_csv("data/clean_trip_analysis.csv")

df = raw.merge(clean, on="TRIP_ID")

print("Trips compared:", len(df))
print("Trips with flagged segments:",
      (df["FLAGGED_SEGMENTS"] > 0).sum())

print("\nRaw vs cleaned average speed:")
print("Raw mean:", round(raw["AVG_SPEED_KMH"].mean(), 2), "km/h")
print("Cleaned mean:", round(
    clean["CLEAN_AVG_SPEED_KMH"].mean(), 2), "km/h")

print("\nLargest distance reductions:")
df["DISTANCE_REDUCTION_KM"] = (
    df["DISTANCE_KM"] - df["CLEAN_DISTANCE_KM"]
)

print(
    df.sort_values("DISTANCE_REDUCTION_KM", ascending=False)[
        ["TRIP_ID", "DISTANCE_KM", "CLEAN_DISTANCE_KM",
         "DISTANCE_REDUCTION_KM", "FLAGGED_SEGMENTS"]
    ].head(10).to_string(index=False)
)

plt.figure(figsize=(9, 5))
plt.scatter(
    df["AVG_SPEED_KMH"],
    df["CLEAN_AVG_SPEED_KMH"],
    alpha=0.7
)
plt.xlabel("Raw average speed (km/h)")
plt.ylabel("Cleaned average speed (km/h)")
plt.title("Raw vs Cleaned Trip Speeds")
plt.tight_layout()
plt.savefig("data/raw_vs_cleaned_speed.png")
plt.show()

print("\nChart saved to data/raw_vs_cleaned_speed.png")