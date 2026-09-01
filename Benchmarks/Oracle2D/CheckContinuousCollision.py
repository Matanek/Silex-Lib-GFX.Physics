#!/usr/bin/env python3
"""Compare pinned Box2D and public Silex continuous-collision witnesses."""

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


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 3:
        print(
            "usage: CheckContinuousCollision.py BOX2D_RECORDS SILEX_RECORDS",
            file=sys.stderr,
        )
        return 2
    reference = read_records(pathlib.Path(sys.argv[1]))
    candidate = read_records(pathlib.Path(sys.argv[2]))
    expected_names = {
        "fixed_circle", "fixed_capsule", "fixed_segment", "fixed_polygon",
        "kinematic_target", "dynamic_bullet",
    }
    if reference.keys() != candidate.keys() or reference.keys() != expected_names:
        return fail("continuous-collision case sets differ")

    for engine, records in (("Box2D", reference), ("Silex", candidate)):
        for name, values in records.items():
            if len(values) != 4 or not all(math.isfinite(value) for value in values):
                return fail(f"{engine} {name}: expected four finite state fields")

    for name in ("fixed_circle", "fixed_capsule", "fixed_segment", "fixed_polygon"):
        expected = reference[name]
        actual = candidate[name]
        if expected[0] >= 0.0 or actual[0] >= 0.0:
            return fail(f"{name}: an engine tunneled through the fixed wall")
        if abs(expected[0] - actual[0]) > 0.002:
            return fail(
                f"{name}: Box2D TOI x={expected[0]:.9g} "
                f"Silex TOI x={actual[0]:.9g}"
            )
        if expected[1] < 299.0 or actual[1] >= 299.0:
            return fail(f"{name}: unexpected one-step response classification")

    expected_kinematic = reference["kinematic_target"]
    actual_kinematic = candidate["kinematic_target"]
    if abs(expected_kinematic[2] - actual_kinematic[2]) > 0.002:
        return fail("kinematic_target: target integration differs")
    if abs(expected_kinematic[1]) > 1.0 or actual_kinematic[1] <= 250.0:
        return fail("kinematic_target: unexpected relative-motion response classification")

    expected_bullet = reference["dynamic_bullet"]
    actual_bullet = candidate["dynamic_bullet"]
    if abs(expected_bullet[0] - actual_bullet[0]) > 0.002:
        return fail("dynamic_bullet: TOI position differs")
    if expected_bullet[3] > 1.0 or actual_bullet[3] <= 1.0:
        return fail("dynamic_bullet: unexpected one-step impulse classification")

    print("continuous-collision oracle compared 6 cases and 3 response divergences")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
