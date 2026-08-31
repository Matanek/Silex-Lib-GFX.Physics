#!/usr/bin/env python3
"""Compare pinned Box2D and Silex contact-policy witnesses."""

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
        print("usage: CheckContactPolicies.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    expected = records(pathlib.Path(sys.argv[1]))
    actual = records(pathlib.Path(sys.argv[2]))
    if expected.keys() != actual.keys():
        print("contact-policy case sets differ", file=sys.stderr)
        return 1
    for name, left_values in expected.items():
        right_values = actual[name]
        tolerance = 0.01
        if name == "normal":
            tolerance = 0.07
        if len(left_values) != len(right_values):
            print(f"{name}: field counts differ", file=sys.stderr)
            return 1
        for index, (left, right) in enumerate(zip(left_values, right_values)):
            if not math.isfinite(right) or abs(left - right) > tolerance:
                print(
                    f"{name}[{index}]: Box2D={left:.9g} Silex={right:.9g}",
                    file=sys.stderr,
                )
                return 1
    print(f"contact-policy oracle matched {len(expected)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
