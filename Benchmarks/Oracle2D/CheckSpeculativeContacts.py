#!/usr/bin/env python3
"""Compare the complete speculative-contact corpus with fixed tolerances."""
import math
from pathlib import Path
import sys

TOLERANCES = (0, 1e-4, 1e-4, 1e-3, 0, 0, 0, 0, 0, 1e-4, 2e-3)
INTEGER_COLUMNS = (0, 4, 5, 6, 7, 8)
REQUIRED = {f'spec_{family}_{gap}_{speed}_{substeps}_{step}_{timing}'
            for family in range(4) for gap in range(4) for speed in range(4)
            for substeps in (1, 4) for step in range(6) for timing in range(2)}


def records(path):
    result = {}
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split()
        if len(fields) != 12:
            raise ValueError(f'wrong field count on line {number}')
        key, *raw = fields
        if key in result:
            raise ValueError(f'duplicate case: {key}')
        values = tuple(map(float, raw))
        if not all(map(math.isfinite, values)):
            raise ValueError(f'non-finite case: {key}')
        if any(values[i] < 0 or not values[i].is_integer() for i in INTEGER_COLUMNS):
            raise ValueError(f'invalid count: {key}')
        result[key] = values
    if result.keys() != REQUIRED:
        raise ValueError('incomplete or unexpected case set')
    return result


def compare(expected, actual):
    if expected.keys() != REQUIRED or actual.keys() != REQUIRED:
        raise ValueError('incomplete or unexpected case set')
    for key in sorted(REQUIRED):
        for values in (expected[key], actual[key]):
            if len(values) != 11 or not all(map(math.isfinite, values)):
                raise ValueError(f'invalid values: {key}')
        for column, tolerance in enumerate(TOLERANCES):
            if abs(expected[key][column] - actual[key][column]) > tolerance:
                raise ValueError(f'{key}, field {column}: Box2D={expected[key][column]} '
                                 f'Silex={actual[key][column]}, tolerance={tolerance}')
    return len(REQUIRED)


if __name__ == '__main__':
    count = compare(records(sys.argv[1]), records(sys.argv[2]))
    print(f'speculative contacts matched {count} samples')
