
# Porto study-area boundaries
MIN_LON = -9.0
MAX_LON = -8.3
MIN_LAT = 40.8
MAX_LAT = 41.4

def is_valid_coordinate(lon, lat):
    return (
        MIN_LON <= lon <= MAX_LON
        and MIN_LAT <= lat <= MAX_LAT
    )

# Test cases: (longitude, latitude, expected result)
test_cases = [
    (-8.61, 41.15, True),    # Inside Porto
    (-9.10, 41.15, False),   # Longitude too far west
    (-8.61, 41.50, False),   # Latitude too far north
    (-8.20, 41.15, False),   # Longitude too far east
    (-8.61, 40.70, False),   # Latitude too far south
]

for lon, lat, expected in test_cases:
    actual = is_valid_coordinate(lon, lat)
    print(
        f"Coordinates ({lon}, {lat}): "
        f"Expected={expected}, Actual={actual}"
    )
    assert actual == expected

print("UT-04 PASSED")
