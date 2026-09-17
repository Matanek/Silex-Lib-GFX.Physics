#!/usr/bin/env python3
"""Compare complete motor/mouse transients with fixed numeric criteria."""
import math
from pathlib import Path
import sys

REQUIRED = {f"target_{family}_{geometry}_{variant}_{substeps}_{step}"
    for family in range(2) for geometry in range(3) for variant in range(8)
    for substeps in (1, 2, 4, 8) for step in range(8)}
TOLERANCES = (1e-4,) * 3 + (1e-3,) * 3 + (1e-4,) * 3 + (1e-3,) * 3 + (2e-3,) * 3


def validate(data):
    if data.keys() != REQUIRED:
        raise ValueError("missing or unexpected motor/mouse case")
    for key, row in data.items():
        if len(row) != 15 or not all(map(math.isfinite, row)):
            raise ValueError(f"invalid values: {key}")
        _, family, geometry, variant, substeps, step = key.split("_")
        maximum_force = 1 if variant == "0" else 0 if variant == "2" else 1000
        maximum_torque = maximum_force
        if variant == "4" or (variant == "5" and int(step) >= 3):
            maximum_force, maximum_torque = 20, 5
        if math.hypot(row[12], row[13]) > maximum_force + 2e-3:
            raise ValueError(f"force cap violated: {key}")
        if family == "0" and abs(row[14]) > maximum_torque + 2e-3:
            raise ValueError(f"motor torque cap violated: {key}")
        if variant == "7" and abs(row[11]) > 1e-6:
            raise ValueError(f"fixed body rotated: {key}")


def records(path):
    data = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 16 or fields[0] in data:
            raise ValueError("invalid or duplicate motor/mouse record")
        data[fields[0]] = tuple(map(float, fields[1:]))
    validate(data)
    return data


def compare(expected, actual):
    validate(expected)
    validate(actual)
    for key in sorted(REQUIRED):
        for column, (left, right, tolerance) in enumerate(zip(expected[key], actual[key], TOLERANCES)):
            if abs(left - right) > tolerance:
                raise ValueError(f"{key}, field {column}: Box2D={left}, Silex={right}, tolerance={tolerance}")
    return len(REQUIRED)


if __name__ == "__main__":
    count = compare(records(sys.argv[1]), records(sys.argv[2]))
    print(f"motor/mouse response matched {count} observations")
