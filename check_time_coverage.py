
import pandas as pd

df = pd.read_csv("data/train.csv", nrows=100)

df["DATETIME"] = pd.to_datetime(
    df["TIMESTAMP"], unit="s", utc=True
).dt.tz_convert("Europe/Lisbon")

df["HOUR"] = df["DATETIME"].dt.hour

print("Total rows:", len(df))
print("\nTrips per departure hour:")
print(df["HOUR"].value_counts().sort_index().to_string())

print("\nTimestamp range:")
print("First:", df["DATETIME"].min())
print("Last: ", df["DATETIME"].max())