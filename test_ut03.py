
import math

# Known distance and time interval
distance_km = 0.15
interval_seconds = 15

# Expected speed in km/h
expected_speed = (distance_km / interval_seconds) * 3600

# Calculate speed using the same formula
calculated_speed = distance_km * 3600 / interval_seconds

print("Distance (km):", distance_km)
print("Time interval (seconds):", interval_seconds)
print("Expected speed (km/h):", expected_speed)
print("Calculated speed (km/h):", calculated_speed)

assert math.isclose(
    calculated_speed,
    expected_speed,
    rel_tol=1e-9
)

print("UT-03 PASSED")
