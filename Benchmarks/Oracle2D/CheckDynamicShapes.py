#!/usr/bin/env python3
"""Compare pinned Box2D and public Silex dynamic-shape witnesses."""

from __future__ import annotations

import math
import pathlib
import sys


def read_records(path: pathlib.Path) -> dict[str, list[float]]:
    records: dict[str, list[float]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        fields = raw_line.split()
        if fields:
            records[fields[0]] = [float(field) for field in fields[1:]]
    return records


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: CheckDynamicShapes.py BOX2D_RECORDS SILEX_RECORDS",
            file=sys.stderr,
        )
        return 2
    reference = read_records(pathlib.Path(sys.argv[1]))
    candidate = read_records(pathlib.Path(sys.argv[2]))
    if reference.keys() != candidate.keys():
        print("dynamic-shape case sets differ", file=sys.stderr)
        return 1
    for name, expected in reference.items():
        actual = candidate[name]
        if len(expected) != 6 or len(actual) != 6:
            print(f"{name}: expected six state fields", file=sys.stderr)
            return 1
        if not all(math.isfinite(value) for value in actual):
            print(f"{name}: Silex emitted a non-finite state", file=sys.stderr)
            return 1
        compared_fields = 2 if name == "chain_transition" else 4
        for index in range(compared_fields):
            if abs(expected[index] - actual[index]) > 0.08:
                print(
                    f"{name}[{index}]: Box2D={expected[index]:.9g} "
                    f"Silex={actual[index]:.9g}",
                    file=sys.stderr,
                )
                return 1
        if name == "chain_transition":
            if actual[0] >= 0.0 or actual[1] <= 0.7:
                print(f"{name}: circle did not cross the internal vertices", file=sys.stderr)
                return 1
        elif abs(actual[3]) > 0.05:
            print(f"{name}: vertical speed did not settle", file=sys.stderr)
            return 1
    if len(reference) != 8:
        print(f"expected eight dynamic-shape cases, got {len(reference)}", file=sys.stderr)
        return 1
    print(f"dynamic-shape oracle matched {len(reference)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
