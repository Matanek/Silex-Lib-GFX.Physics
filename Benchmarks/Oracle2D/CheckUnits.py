#!/usr/bin/env python3
"""Compare canonical physical observations and scale invariance independently."""
import math
import pathlib
import sys

# Count and per-field physical tolerances fixed before measuring the witnesses.
TOLERANCES = {
    'rest': (0.003, 0.003, 0),
    'ray': (0.002, 0.002),
    'cast': (0.002, 0.002),
    # The existing CCD witness separately classifies post-TOI velocity.
    'ccd': (0.002, None),
    'low': (0.05, 0),
    'high': (0.05, 0),
    'sleep_low': (0,),
    'sleep_high': (0,),
    'limits': (0.001, 0.000001, 0.000001, 0.000001, 0.000001),
}


def read(path):
    result = {}
    for line in pathlib.Path(path).read_text().splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0] in result:
            raise ValueError(f'duplicate record {fields[0]}')
        result[fields[0]] = [float({'true': '1', 'false': '0'}.get(v, v)) for v in fields[1:]]
    return result


def validate(reference, candidate):
    keys = {scale + '_' + case for scale in ('meter', 'centimeter') for case in TOLERANCES}
    for label, records in [('Box2D', reference), ('Silex', candidate)]:
        if records.keys() != keys:
            raise ValueError(f'{label}: expected all eighteen scale observations')
        for key, values in records.items():
            case = key.split('_', 1)[1]
            if len(values) != len(TOLERANCES[case]) or not all(map(math.isfinite, values)):
                raise ValueError(f'{label} {key}: invalid finite field set')
        for case in TOLERANCES:
            for first, second in zip(records['meter_' + case], records['centimeter_' + case]):
                if abs(first - second) > 1e-4:
                    raise ValueError(f'{label} {case}: scale changes normalized physics ({first}, {second})')
        for scale in ('meter', 'centimeter'):
            if records[scale+'_sleep_low'] != [0] or records[scale+'_sleep_high'] != [1]:
                raise ValueError(f'{label}: sleep threshold was not exercised')
            if records[scale+'_low'][1] != 0 or records[scale+'_high'][1] != 1:
                raise ValueError(f'{label}: hit threshold was not exercised')
            if abs(records[scale+'_low'][0]) > 0.05 or records[scale+'_high'][0] < 1.95:
                raise ValueError(f'{label}: restitution threshold was not exercised')
            if abs(records[scale+'_limits'][0] - 400) > 0.001:
                raise ValueError(f'{label}: speed cap was not exercised')
    for key in keys:
        case = key.split('_', 1)[1]
        for index, tolerance in enumerate(TOLERANCES[case]):
            if tolerance is not None and abs(reference[key][index] - candidate[key][index]) > tolerance:
                raise ValueError(f'{key}[{index}]: Box2D={reference[key][index]} Silex={candidate[key][index]}')


def main():
    if len(sys.argv) != 3:
        print('usage: CheckUnits.py BOX2D_RECORDS SILEX_RECORDS', file=sys.stderr)
        return 2
    try:
        validate(read(sys.argv[1]), read(sys.argv[2]))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1
    print('units oracle matched 18 observations; both scales invariant')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
