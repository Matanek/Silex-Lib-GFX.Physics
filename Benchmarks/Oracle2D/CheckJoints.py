#!/usr/bin/env python3
"""Compare pinned Box2D and Silex joint behavior witnesses."""

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
        print("usage: CheckJoints.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    expected = records(pathlib.Path(sys.argv[1]))
    actual = records(pathlib.Path(sys.argv[2]))
    required = {"distance", "prismatic", "revolute", "wheel"}
    if expected.keys() != required or actual.keys() != required:
        print("joint oracle case sets differ", file=sys.stderr)
        return 1
    for name in sorted(required):
        left = expected[name]
        right = actual[name]
        if len(left) != 4 or len(right) != 4 or not all(map(math.isfinite, right)):
            print(f"{name}: invalid field set", file=sys.stderr)
            return 1
        # Position/translation/angle are the cross-engine contract. Forces are
        # checked for finiteness and configured bounds because the two native
        # Soft Step implementations deliberately have different impulse caches.
        tolerance = 0.08 if name != "wheel" else 0.15
        if abs(left[0] - right[0]) > tolerance:
            print(f"{name}: Box2D={left[0]:.9g} Silex={right[0]:.9g}", file=sys.stderr)
            return 1
        if name == "prismatic" and abs(right[2]) > 40.01:
            print("prismatic motor force exceeded configured maximum", file=sys.stderr)
            return 1
        if name in {"revolute", "wheel"} and abs(right[3]) > 20.01:
            print(f"{name} motor torque exceeded configured maximum", file=sys.stderr)
            return 1
    print("joint oracle matched 4 runtime cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
