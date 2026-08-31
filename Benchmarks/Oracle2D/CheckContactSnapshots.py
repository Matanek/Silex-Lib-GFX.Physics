#!/usr/bin/env python3
"""Compare pinned Box2D and Silex collider-level contact snapshots."""

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
        print("usage: CheckContactSnapshots.py BOX2D_RECORDS SILEX_RECORDS", file=sys.stderr)
        return 2
    expected = records(pathlib.Path(sys.argv[1]))
    actual = records(pathlib.Path(sys.argv[2]))
    required = {"contact", "floor", "begin", "end", "sensor"}
    if expected.keys() != required or actual.keys() != required:
        print("contact snapshot case sets differ", file=sys.stderr)
        return 1

    for name in ("floor", "begin", "end", "sensor"):
        if expected[name] != actual[name]:
            print(f"{name}: Box2D={expected[name]} Silex={actual[name]}", file=sys.stderr)
            return 1

    left = expected["contact"]
    right = actual["contact"]
    if len(left) != 10 or len(right) != 10:
        print("contact: field counts differ", file=sys.stderr)
        return 1
    if left[:8] != right[:8]:
        print(f"contact metadata: Box2D={left[:8]} Silex={right[:8]}", file=sys.stderr)
        return 1
    for name, values in (("Box2D", left[8:]), ("Silex", right[8:])):
        if any(not math.isfinite(value) or value <= 0.0 for value in values):
            print(f"{name}: expected two positive finite normal impulses", file=sys.stderr)
            return 1
    left_total = sum(left[8:])
    right_total = sum(right[8:])
    if abs(left_total - right_total) > 0.35:
        print(
            f"normal impulse total: Box2D={left_total:.9g} Silex={right_total:.9g}",
            file=sys.stderr,
        )
        return 1
    print("contact snapshot oracle matched 5 cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
