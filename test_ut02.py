
import json

test_cases = [
    ("empty string", ""),
    ("empty list", "[]"),
    ("malformed JSON", "[[-8.61, 41.15],"),
]

for name, polyline in test_cases:
    try:
        points = json.loads(polyline)

        if not isinstance(points, list) or len(points) < 2:
            print(f"{name}: handled safely")
            continue

        print(f"{name}: parsed successfully")

    except (json.JSONDecodeError, TypeError):
        print(f"{name}: handled safely")

print("UT-02 test completed")
