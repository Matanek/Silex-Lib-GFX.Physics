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


def polygon_has_supported_face(angle: float) -> bool:
    vertices = ((-0.5, -0.4), (0.5, -0.4), (0.42, 0.45), (-0.42, 0.45))
    sine = math.sin(angle)
    cosine = math.cos(angle)
    for index, first in enumerate(vertices):
        second = vertices[(index + 1) % len(vertices)]
        edge_x = second[0] - first[0]
        edge_y = second[1] - first[1]
        world_y = sine * edge_x + cosine * edge_y
        if abs(world_y) <= 0.005:
            return True
    return False


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
        if name.startswith("example_"):
            compared_fields = 0
        elif name.startswith("conveyor_"):
            compared_fields = 6
        for index in range(compared_fields):
            if abs(expected[index] - actual[index]) > 0.08:
                print(
                    f"{name}[{index}]: Box2D={expected[index]:.9g} "
                    f"Silex={actual[index]:.9g}",
                    file=sys.stderr,
                )
                return 1
        if name == "example_capsule_impact":
            for index in range(2):
                if abs(expected[index] - actual[index]) > 0.02:
                    print(
                        f"{name}[{index}]: Box2D={expected[index]:.9g} "
                        f"Silex={actual[index]:.9g}",
                        file=sys.stderr,
                    )
                    return 1
            if abs(actual[2]) > 0.05 or abs(actual[3]) > 0.05:
                print(f"{name}: capsule did not settle", file=sys.stderr)
                return 1
        elif name == "example_polygon_settle":
            if not 0.45 <= actual[1] <= 0.75 or not polygon_has_supported_face(actual[4]):
                print(f"{name}: polygon is not supported by a face", file=sys.stderr)
                return 1
            if abs(actual[2]) > 0.05 or abs(actual[3]) > 0.05 or abs(actual[5]) > 0.05:
                print(f"{name}: polygon did not settle", file=sys.stderr)
                return 1
        elif name == "example_segment_settle":
            if abs(actual[1]) > 0.02 or abs(math.sin(actual[4])) > 0.005:
                print(f"{name}: segment did not settle flat", file=sys.stderr)
                return 1
            if abs(actual[2]) > 0.05 or abs(actual[3]) > 0.05 or abs(actual[5]) > 0.05:
                print(f"{name}: segment did not settle", file=sys.stderr)
                return 1
        elif name == "chain_transition":
            if actual[0] >= 0.0 or actual[1] <= 0.7:
                print(f"{name}: circle did not cross the internal vertices", file=sys.stderr)
                return 1
        elif name == "conveyor_from_rest":
            if actual[2] <= 0.0 or actual[5] <= 0.0:
                print(f"{name}: conveyor did not induce its expected motion", file=sys.stderr)
                return 1
        elif name == "conveyor_rolls_fast_circle":
            if actual[2] <= 0.0 or actual[5] >= 0.0:
                print(f"{name}: rightward rolling has the wrong sign", file=sys.stderr)
                return 1
            contact_speed = actual[2] + actual[5] * 0.35
            if abs(contact_speed - 0.85) > 0.03:
                print(
                    f"{name}: contact={contact_speed:.9g} belt=0.85",
                    file=sys.stderr,
                )
                return 1
        elif abs(actual[3]) > 0.05:
            print(f"{name}: vertical speed did not settle", file=sys.stderr)
            return 1
    if len(reference) != 13:
        print(f"expected thirteen dynamic-shape cases, got {len(reference)}", file=sys.stderr)
        return 1
    print(f"dynamic-shape oracle matched {len(reference)} cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
