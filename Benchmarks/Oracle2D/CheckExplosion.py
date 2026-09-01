#!/usr/bin/env python3
"""Compare the pinned Box2D and public Silex radial-explosion witnesses."""

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
        print("usage: CheckExplosion.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    reference = records(pathlib.Path(sys.argv[1]))
    candidate = records(pathlib.Path(sys.argv[2]))
    expected_names = {"count", "near", "far", "rejected"}
    if reference.keys() != candidate.keys() or set(reference) != expected_names:
        print("explosion case sets differ", file=sys.stderr)
        return 1
    for name in expected_names:
        if len(reference[name]) != len(candidate[name]) or not all(
            math.isfinite(value) for value in candidate[name]
        ):
            print(f"{name}: invalid candidate record", file=sys.stderr)
            return 1
    if candidate["count"] != [2.0]:
        print("Silex explosion did not retain two selected bodies", file=sys.stderr)
        return 1
    if any(abs(value) > 1.0e-6 for value in candidate["rejected"]):
        print("Silex explosion affected the filtered body", file=sys.stderr)
        return 1
    if candidate["near"][0] <= candidate["far"][0] or candidate["far"][0] <= 0.0:
        print("Silex explosion attenuation trend is invalid", file=sys.stderr)
        return 1
    for name in ("near", "far", "rejected"):
        for index, expected in enumerate(reference[name]):
            if abs(expected - candidate[name][index]) > 0.003:
                print(
                    f"{name}[{index}]: Box2D={expected:.9g} "
                    f"Silex={candidate[name][index]:.9g}",
                    file=sys.stderr,
                )
                return 1
    print("radial-explosion oracle matched positions, directions, filtering, and attenuation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
