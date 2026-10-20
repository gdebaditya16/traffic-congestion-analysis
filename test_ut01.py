
import json

# Test trajectory containing exactly two valid GPS points
polyline = '[[-8.6100, 41.1500], [-8.6090, 41.1500]]'

points = json.loads(polyline)

total_segments = 0

for i in range(1, len(points)):
    lon1, lat1 = points[i - 1]
    lon2, lat2 = points[i]

    # Same geographic bounds as build_clean_segments.py
    valid_coordinates = (
        -9.0 <= lon1 <= -8.3
        and 40.8 <= lat1 <= 41.4
        and -9.0 <= lon2 <= -8.3
        and 40.8 <= lat2 <= 41.4
    )

    if valid_coordinates:
        total_segments += 1

print("Number of GPS points:", len(points))
print("Segments created:", total_segments)

assert len(points) == 2
assert total_segments == 1

print("UT-01 PASSED")
