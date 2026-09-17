#!/usr/bin/env python3
"""Qualify immediate filtering without hiding pinned Box2D lifecycle differences."""
import math
from pathlib import Path
import sys

REQUIRED = {f"filter_{scene}_{stage}" for scene in range(3) for stage in range(8)}
TOLERANCES = (0, 0, 0, 0, 0, 0, 1e-4, 1e-3, 2e-3)
RAW_DIFFERENCES = {"filter_0_5", "filter_0_6", "filter_1_1", "filter_1_2",
                   "filter_1_3", "filter_1_5", "filter_1_6", "filter_2_5", "filter_2_6"}


def validate(data):
    if data.keys() != REQUIRED:
        raise ValueError("missing or unexpected filter stage")
    for key, values in data.items():
        if len(values) != 9 or not all(map(math.isfinite, values)):
            raise ValueError(f"invalid values: {key}")
        if any(v < 0 or not float(v).is_integer() for v in values[:6]):
            raise ValueError(f"invalid count or identity mask: {key}")


def records(path):
    data = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 10 or fields[0] in data:
            raise ValueError("invalid or repeated filter record")
        data[fields[0]] = tuple(map(float, fields[1:]))
    validate(data)
    return data


def differs(first, second):
    return any(abs(a - b) > t for a, b, t in zip(first, second, TOLERANCES))


def compare(raw, immediate, actual):
    for data in (raw, immediate, actual):
        validate(data)
    differences = {key for key in REQUIRED if differs(raw[key], immediate[key])}
    if differences != RAW_DIFFERENCES:
        raise ValueError(f"pinned raw lifecycle changed: {sorted(differences)}")
    # Existing contacts stop the body in the raw reference after filter creation.
    if raw["filter_1_1"][4:6] != (2, 3) or abs(raw["filter_1_1"][7]) > 1e-3:
        raise ValueError("raw filter no longer retains its existing collision response")
    if immediate["filter_1_1"][2:6] != (2, 3, 0, 0) or abs(immediate["filter_1_1"][7] + 2) > 1e-3:
        raise ValueError("immediate filter did not remove response and publish exact ends")
    for scene in range(3):
        key = f"filter_{scene}_5"
        if raw[key][4] != 0 or immediate[key][:6] != (2, 3, 0, 0, 2, 3):
            raise ValueError("destruction no longer distinguishes rediscovery policies")
    for key in sorted(REQUIRED):
        for column, (expected, value, tolerance) in enumerate(zip(immediate[key], actual[key], TOLERANCES)):
            if abs(expected - value) > tolerance:
                raise ValueError(f"{key}, field {column}: immediate Box2D={expected}, Silex={value}")
    return len(REQUIRED)


if __name__ == "__main__":
    count = compare(*(records(path) for path in sys.argv[1:]))
    print(f"immediate filter lifecycle matched {count} stages; {len(RAW_DIFFERENCES)} raw Box2D differences preserved")
