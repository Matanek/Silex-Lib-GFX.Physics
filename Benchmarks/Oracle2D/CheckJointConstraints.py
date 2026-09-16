#!/usr/bin/env python3
"""Compare complete joint corpora using the fixed Task16 absolute tolerances."""
import math
from pathlib import Path
import sys

TOLERANCES = (0.0001,) * 3 + (0.001,) * 3 + (0.002,) * 3


def required_keys(corpus):
    if corpus == 'tuning':
        prefix, families, variants = 'rigid', 4, 7
    elif corpus == 'combinations':
        prefix, families, variants = 'combination', 5, 8
    else:
        raise ValueError(f'unknown corpus: {corpus}')
    return {f'{prefix}_{family}_{variant}_{substeps}_{step}_{geometry}'
            for family in range(families) for variant in range(variants)
            for substeps in (1, 2, 4, 8) for step in range(8) for geometry in range(3)}


def records(path):
    result = {}
    for number, line in enumerate(Path(path).read_text().splitlines(), 1):
        fields = line.split()
        if len(fields) != 10:
            raise ValueError(f'invalid field count on line {number}')
        key, *raw = fields
        if key in result:
            raise ValueError(f'duplicate case: {key}')
        values = tuple(map(float, raw))
        if not all(map(math.isfinite, values)):
            raise ValueError(f'non-finite value: {key}')
        result[key] = values
    return result


def compare(expected, actual, corpus):
    required = required_keys(corpus)
    if expected.keys() != required or actual.keys() != required:
        raise ValueError(f'{corpus} case sets differ')
    for key in sorted(required):
        for values in (expected[key], actual[key]):
            if len(values) != len(TOLERANCES) or not all(map(math.isfinite, values)):
                raise ValueError(f'invalid values: {key}')
        for column, tolerance in enumerate(TOLERANCES):
            if abs(expected[key][column] - actual[key][column]) > tolerance:
                raise ValueError(f'{key}, field {column}: Box2D={expected[key][column]} '
                                 f'Silex={actual[key][column]}, tolerance={tolerance}')
    return len(required)


if __name__ == '__main__':
    count = compare(records(sys.argv[2]), records(sys.argv[3]), sys.argv[1])
    print(f'joint {sys.argv[1]} matched {count} transient samples')
