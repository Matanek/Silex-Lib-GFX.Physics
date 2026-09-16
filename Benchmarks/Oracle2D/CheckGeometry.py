#!/usr/bin/env python3
"""Compare the pinned Box2D and public Silex geometry witnesses."""

from __future__ import annotations

import math
import pathlib
import sys


def read_records(path: pathlib.Path) -> dict[str, list[float]]:
    records: dict[str, list[float]] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        fields = raw_line.split()
        if not fields:
            continue
        values = []
        for field in fields[1:]:
            if field == "true":
                values.append(1.0)
            elif field == "false":
                values.append(0.0)
            else:
                values.append(float(field))
        if fields[0] in records:
            raise ValueError(f"duplicate geometry case: {fields[0]}")
        records[fields[0]] = values
    return records


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: CheckGeometry.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    reference = read_records(pathlib.Path(sys.argv[1]))
    candidate = read_records(pathlib.Path(sys.argv[2]))
    if reference.keys() != candidate.keys():
        print("geometry case sets differ", file=sys.stderr)
        return 1
    required = {"segment_circle", "capsule_capsule", "segment_capsule"}
    if not required <= reference.keys() or len(reference) != 11:
        print("expected eleven geometry cases including the three contact pairs", file=sys.stderr)
        return 1
    for name, expected in reference.items():
        actual = candidate[name]
        if len(expected) != len(actual):
            print(f"{name}: field counts differ", file=sys.stderr)
            return 1
        if name in {"segment_circle", "capsule_capsule", "segment_capsule"}:
            count = 1 if name == "segment_circle" else 2
            if len(actual) != 3 + 3 * count or expected[0] != count or actual[0] != count:
                print(f"{name}: unexpected manifold point count", file=sys.stderr)
                return 1
        for index, (left, right) in enumerate(zip(expected, actual)):
            tolerance = 0.003 if name not in {"hull", "degenerate_hull"} else 0.0001
            if not math.isfinite(left) or not math.isfinite(right) or abs(left - right) > tolerance:
                print(
                    f"{name}[{index}]: Box2D={left:.9g} Silex={right:.9g}",
                    file=sys.stderr,
                )
                return 1
    print(f"geometry oracle matched {len(reference)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
