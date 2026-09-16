#!/usr/bin/env python3
import math
from pathlib import Path
import sys

# Fixed before the paired trajectory: 3 linear slops, 0.002 rad, 0.02 m/s.
SUPPORT_TOLERANCES = (0.015, 0.015, 0.002, 0.02, 0.02)


def records(path):
    result = {}
    expected = {f'stage_{i}': 8 for i in range(24)}
    expected.update({f'precontact_{i}': 2 for i in range(4)}, support=7)
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if not fields or fields[0] in result or fields[0] not in expected:
            raise ValueError('unknown or duplicate contact record')
        name = fields[0]
        if len(fields) != expected[name] + 1:
            raise ValueError('invalid contact record width')
        if name == 'support':
            values = tuple(map(int, fields[1:3])) + tuple(map(float, fields[3:]))
        else:
            values = tuple(map(int, fields[1:]))
        if not all(math.isfinite(v) for v in values):
            raise ValueError('nonfinite contact record')
        result[name] = values
    if result.keys() != expected.keys():
        raise ValueError('incomplete contact scenario')
    return result


def compare(expected, actual):
    if expected.keys() != actual.keys():
        raise ValueError('scenario keys differ')
    for name, values in expected.items():
        observed = actual[name]
        if name != 'support':
            if observed != values:
                raise ValueError(f'{name}: Box2D={values}, Silex={observed}')
        else:
            if values[:2] != (2, 3) or observed[:2] != (2, 3):
                raise ValueError('both surfaces must support the body')
            for index, tolerance in enumerate(SUPPORT_TOLERANCES, 2):
                if not math.isfinite(observed[index]) or abs(values[index] - observed[index]) > tolerance:
                    raise ValueError(f'support field {index}: {values[index]} != {observed[index]}')


if __name__ == '__main__':
    compare(records(sys.argv[1]), records(sys.argv[2]))
    print('compound contacts matched 24 event stages, 4 precontact stages and two-surface support')
