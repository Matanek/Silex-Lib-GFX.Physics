#!/usr/bin/env python3
"""Check the declared geometric value corpus with tolerances fixed before implementation."""
import math
from pathlib import Path
import sys

def read(path):
    records = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if fields[0] in records:
            raise ValueError('duplicate record: ' + fields[0])
        records[fields[0]] = list(map(float, fields[1:]))
    expected = {f'{kind}_{shift}_{case}_{shape}' for kind in ['ray', 'cast']
                for shift in range(2) for case in range(18) for shape in range(5)}
    if records.keys() != expected:
        raise ValueError('expected exactly 360 ray and shape cast records')
    return records

def compare(reference, candidate):
    if reference.keys() != candidate.keys():
        raise ValueError("geometry value case sets differ")
    failures = []
    for key, left in reference.items():
        right = candidate[key]
        if len(left) != 6 or len(right) != 6:
            raise ValueError(key + ': expected six fields')
        for index, (a, b) in enumerate(zip(left, right)):
            exact = index == 0 or (left[1] == 0 and a == 0 and index in [1, 4, 5])
            if not math.isfinite(a) or not math.isfinite(b) or (a != b if exact else not math.isclose(a, b, abs_tol=2e-5, rel_tol=2e-6)):
                failures.append(f'{key}[{index}]: Box2D={a:.9g} Silex={b:.9g}')
    if failures:
        raise ValueError('\n'.join(failures))


def main():
    if len(sys.argv) != 3:
        raise SystemExit('usage: CheckGeometryValues.py BOX2D_RECORDS SILEX_RECORDS')
    try:
        compare(*map(read, sys.argv[1:]))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print('geometric values oracle matched 360 cases')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
