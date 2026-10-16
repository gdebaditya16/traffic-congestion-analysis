
import pandas as pd

df = pd.read_csv("data/trip_analysis.csv")

print("Total trips:", len(df))

print("\nSpeed statistics:")
print(df["AVG_SPEED_KMH"].describe())

print("\nTrips with average speed above 80 km/h:")
print(
    df[df["AVG_SPEED_KMH"] > 80][
        ["TRIP_ID", "DISTANCE_KM", "DURATION_MIN", "AVG_SPEED_KMH"]
    ].to_string(index=False)
)

print("\nTrips with average speed below 5 km/h:")
print(
    df[df["AVG_SPEED_KMH"] < 5][
        ["TRIP_ID", "DISTANCE_KM", "DURATION_MIN", "AVG_SPEED_KMH"]
    ].to_string(index=False)
)