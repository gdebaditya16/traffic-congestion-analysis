
MAX_SPEED_KMH = 120.0

def is_valid_speed(speed_kmh):
    return 0 <= speed_kmh <= MAX_SPEED_KMH

# Test cases: (speed, expected result)
test_cases = [
    (36.0, True),     # Normal speed
    (120.0, True),    # Exactly at the maximum
    (120.1, False),   # Slightly above the maximum
    (150.0, False),   # Excessive speed
    (-5.0, False),    # Negative speed
]

for speed, expected in test_cases:
    actual = is_valid_speed(speed)
    print(
        f"Speed {speed} km/h: "
        f"Expected={expected}, Actual={actual}"
    )
    assert actual == expected

print("UT-05 PASSED")
