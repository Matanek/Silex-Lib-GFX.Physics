#!/usr/bin/env python3
"""Compare pinned Box2D and public Silex world-query witnesses."""

from __future__ import annotations

import math
import pathlib
import sys


def records(path: pathlib.Path) -> dict[str, list[float]]:
    result: dict[str, list[float]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        fields = line.split()
        if fields:
            result[fields[0]] = [float(value) for value in fields[1:]]
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: CheckWorldQueries.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    reference = records(pathlib.Path(sys.argv[1]))
    candidate = records(pathlib.Path(sys.argv[2]))
    if reference.keys() != candidate.keys() or len(reference) != 5:
        print("world-query case sets differ", file=sys.stderr)
        return 1
    tolerances = {
        "aabb": 0.0,
        "overlap_shape": 0.0,
        "ray": 0.002,
        "shape_cast": 0.002,
        "collider": 0.021,
    }
    for name, expected in reference.items():
        actual = candidate[name]
        if len(expected) != len(actual) or not all(math.isfinite(v) for v in actual):
            print(f"{name}: invalid candidate record", file=sys.stderr)
            return 1
        for index, expected_value in enumerate(expected):
            if abs(expected_value - actual[index]) > tolerances[name]:
                print(
                    f"{name}[{index}]: Box2D={expected_value:.9g} "
                    f"Silex={actual[index]:.9g}",
                    file=sys.stderr,
                )
                return 1
    print("world-query oracle matched 5 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
