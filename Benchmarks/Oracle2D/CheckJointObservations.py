#!/usr/bin/env python3
"""Compare current joint observations using fixed absolute tolerances."""
import math
from pathlib import Path
import sys

KEYS = {f"observe_{f}_{g}_{v}_{s}" for f in range(8) for g in range(2)
        for v in range(4) for s in range(8)}
TOLERANCES = (1e-4, 1e-3, 1e-4, 1e-4, 1e-4, 1e-4)


def validate(data):
    if data.keys() != KEYS:
        raise ValueError("missing or unexpected joint observation")
    for key, row in data.items():
        if len(row) != 6 or not all(map(math.isfinite, row)):
            raise ValueError(f"invalid joint observation: {key}")


def records(path):
    data = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 7 or fields[0] in data:
            raise ValueError("invalid or duplicate observation record")
        data[fields[0]] = tuple(map(float, fields[1:]))
    validate(data)
    return data


def compare(reference, actual):
    validate(reference)
    validate(actual)
    for key in sorted(KEYS):
        for column, (left, right, tolerance) in enumerate(zip(reference[key], actual[key], TOLERANCES)):
            if abs(left - right) > tolerance:
                raise ValueError(f"{key}, field {column}: Box2D={left}, Silex={right}, tolerance={tolerance}")
    return len(KEYS)


if __name__ == "__main__":
    print(f"{compare(records(sys.argv[1]), records(sys.argv[2]))} joint observation rows matched")
