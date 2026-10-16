
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/trip_analysis.csv")

# 1. Distribution of average trip speeds
plt.figure(figsize=(9, 5))
plt.hist(df["AVG_SPEED_KMH"], bins=15, edgecolor="black")
plt.xlabel("Average speed (km/h)")
plt.ylabel("Number of trips")
plt.title("Distribution of Average Taxi Trip Speeds")
plt.tight_layout()
plt.savefig("data/speed_distribution.png")
plt.show()

# 2. Distance versus average speed
plt.figure(figsize=(9, 5))
plt.scatter(
    df["DISTANCE_KM"],
    df["AVG_SPEED_KMH"],
    alpha=0.7
)
plt.xlabel("Trip distance (km)")
plt.ylabel("Average speed (km/h)")
plt.title("Trip Distance vs Average Speed")
plt.tight_layout()
plt.savefig("data/distance_vs_speed.png")
plt.show()

print("Charts saved in the data folder.")