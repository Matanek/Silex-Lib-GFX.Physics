#!/usr/bin/env python3
"""Check destruction and explicitly preserve the pinned world-slot reuse difference."""
from pathlib import Path
import sys

KEYS = {f"lifetime_{stage}" for stage in range(4)}


def records(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 12 or fields[0] in result:
            raise ValueError("invalid or duplicate lifetime record")
        if any(value not in ("0", "1") for value in fields[1:]):
            raise ValueError("validity must be a boolean")
        result[fields[0]] = tuple(map(int, fields[1:]))
    return result


def compare(reference, actual):
    for side, data in [("Box2D", reference), ("Silex", actual)]:
        if data.keys() != KEYS:
            raise ValueError(f"{side}: missing or unexpected lifetime stage")
        for stage in range(4):
            # Box2D IDs reuse a world slot without storing its generation.
            # A retained Silex handle remains tied to the finalized store.
            alive = stage in (0, 3) or (side == "Box2D" and stage == 2)
            if data[f"lifetime_{stage}"] != (int(alive),) * 11:
                raise ValueError(f"{side}: invalid lifetime stage {stage}")
    return 44


if __name__ == "__main__":
    count = compare(records(sys.argv[1]), records(sys.argv[2]))
    print(f"{count} validity observations checked; 11 pinned world-slot reuse differences retained")
