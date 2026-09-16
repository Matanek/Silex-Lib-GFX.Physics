#!/usr/bin/env python3
from pathlib import Path
import sys

def records(path):
    result = {}
    for line in Path(path).read_text().splitlines():
        fields = line.split()
        if len(fields) != 10 or fields[0] in result:
            raise ValueError('invalid or duplicate event record')
        result[fields[0]] = tuple(map(int, fields[1:]))
    if result.keys() != {f'stage_{i}' for i in range(10)}:
        raise ValueError('expected ten chronological event stages')
    return result

def compare(expected, actual):
    if expected != actual:
        differences = [f'{name}: Box2D={value}, Silex={actual.get(name)}' for name, value in expected.items() if actual.get(name) != value]
        raise ValueError('\n'.join(differences) or 'event case sets differ')

if __name__ == '__main__':
    compare(records(sys.argv[1]), records(sys.argv[2]))
    print('body event oracle matched ten stages, options and surface identities')
