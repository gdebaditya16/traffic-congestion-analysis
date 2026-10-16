


import pandas as pd
import matplotlib.pyplot as plt

raw = pd.read_csv("data/train.csv", nrows=10000)
clean = pd.read_csv("data/clean_trip_analysis.csv")

raw = raw[["TRIP_ID", "TIMESTAMP"]].copy()

df = raw.merge(clean, on="TRIP_ID", how="inner")

print("Raw rows:", len(raw))
print("Cleaned trips:", len(clean))
print("Matched trips:", len(df))

df["DATETIME"] = pd.to_datetime(
    df["TIMESTAMP"], unit="s", utc=True
).dt.tz_convert("Europe/Lisbon")

df["HOUR"] = df["DATETIME"].dt.hour

hourly = df.groupby("HOUR").agg(
    TRIP_COUNT=("TRIP_ID", "count"),
    AVG_SPEED_KMH=("CLEAN_AVG_SPEED_KMH", "mean"),
    MEDIAN_SPEED_KMH=("CLEAN_AVG_SPEED_KMH", "median")
).reset_index()

print("\nHourly trip analysis:")
print(hourly.to_string(index=False))

hourly.to_csv("data/hourly_analysis.csv", index=False)

plt.figure(figsize=(10, 5))
plt.plot(
    hourly["HOUR"],
    hourly["AVG_SPEED_KMH"],
    marker="o"
)
plt.xticks(range(24))
plt.xlabel("Departure hour (local Porto time)")
plt.ylabel("Mean cleaned trip speed (km/h)")
plt.title("Average Trip Speed by Departure Hour")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("data/hourly_speed.png")
plt.show()

print("\nSaved: data/hourly_analysis.csv")
print("Saved: data/hourly_speed.png")