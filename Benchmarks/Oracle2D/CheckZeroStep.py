#!/usr/bin/env python3
"""Compare zero-duration step observations with the pinned Box2D oracle."""
import math
from pathlib import Path
import sys


def records(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        key, *fields = line.split()
        if key in result:
            raise ValueError(f'duplicate observation: {key}')
        values = tuple(map(float, fields))
        if not all(map(math.isfinite, values)):
            raise ValueError(f'nonfinite observation: {key}')
        result[key] = values
    return result


def compare(expected, actual):
    required = {f'{kind}-{phase}': 7 for kind in ['contact', 'sensor']
                for phase in ['created', 'zero', 'positive', 'paused', 'moved-zero', 'moved-positive']}
    required.update({f'{kind}-{phase}': 2 for kind in ['contact', 'sensor']
                     for phase in ['destroyed-zero', 'destroyed-twice']})
    required.update({f'force-{phase}': 2 for phase in ['zero', 'positive', 'next']})
    if expected.keys() != required.keys() or actual.keys() != required.keys():
        raise ValueError('zero-step observation sets differ')
    for key, count in required.items():
        if len(expected[key]) != count or len(actual[key]) != count:
            raise ValueError(f'invalid field count: {key}')
        tolerance = 0.000001 if key.startswith('force-') else 0.0
        if any(abs(a-b) > tolerance for a, b in zip(expected[key], actual[key])):
            raise ValueError(f'{key}: Box2D={expected[key]} Silex={actual[key]}')


if __name__ == '__main__':
    compare(records(sys.argv[1]), records(sys.argv[2]))
    print('zero-duration step matched 19 observations')
