#!/usr/bin/env python3
"""Compare the pinned Box2D and public Silex body-control witnesses."""

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
        values: list[float] = []
        for field in fields[1:]:
            if field == "true":
                values.append(1.0)
            elif field == "false":
                values.append(0.0)
            else:
                values.append(float(field))
        records[fields[0]] = values
    return records


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: CheckBodyControl.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    reference = read_records(pathlib.Path(sys.argv[1]))
    candidate = read_records(pathlib.Path(sys.argv[2]))
    if reference.keys() != candidate.keys():
        print("body-control case sets differ", file=sys.stderr)
        return 1
    for name, expected in reference.items():
        actual = candidate[name]
        if len(expected) != len(actual):
            print(f"{name}: field counts differ", file=sys.stderr)
            return 1
        for index, (left, right) in enumerate(zip(expected, actual)):
            if not math.isfinite(right) or abs(left - right) > 0.003:
                print(
                    f"{name}[{index}]: Box2D={left:.9g} Silex={right:.9g}",
                    file=sys.stderr,
                )
                return 1
    print(f"body-control oracle matched {len(reference)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
