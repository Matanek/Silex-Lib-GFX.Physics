#!/usr/bin/env python3
"""Compare the distance constraint transient, with fixed absolute tolerances."""
import math
from pathlib import Path
import sys

TOLERANCES = (0.0001, 0.0001, 0.001, 0.002)


def records(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        key, *fields = line.split()
        if key in result:
            raise ValueError(f"duplicate case: {key}")
        values = tuple(map(float, fields))
        if len(values) != 4 or not all(map(math.isfinite, values)):
            raise ValueError(f"invalid fields: {key}")
        result[key] = values
    return result


def compare(expected, actual):
    required = {f"distance-{tuning}-{substeps}-{step}"
                for tuning in range(7) for substeps in (1, 2, 4, 8)
                for step in range(8)}
    if expected.keys() != required or actual.keys() != required:
        raise ValueError("distance tuning case sets differ")
    for key in sorted(required):
        for column, tolerance in enumerate(TOLERANCES):
            if abs(expected[key][column] - actual[key][column]) > tolerance:
                raise ValueError(f"{key}, field {column}: Box2D={expected[key][column]} "
                                 f"Silex={actual[key][column]}, tolerance={tolerance}")


if __name__ == '__main__':
    compare(records(sys.argv[1]), records(sys.argv[2]))
    print("distance constraint tuning matched 224 transient samples")
