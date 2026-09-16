#!/usr/bin/env python3
"""Pair Box2D validity predicates with public Silex construction and diagnostics."""
from pathlib import Path
import subprocess
import sys

reference = [line.split() for line in Path(sys.argv[1]).read_text().splitlines()]
expected = {(family, value) for family in ['scalar', 'vector', 'rotation', 'aabb',
            'aabb-overflow', 'aabb-position', 'ray-origin', 'ray-motion', 'ray-fraction']
            for value in ['zero', 'negative', 'near', 'upper', 'huge', 'inf', 'nan', 'negative-inf']}
raw = {('raw-rotation', 'zero'): 0, ('raw-rotation', 'unit'): 1, ('raw-rotation', 'scaled'): 0,
       ('plane', 'zero-normal'): 0, ('plane', 'unit'): 1, ('plane', 'scaled'): 0,
       ('plane', 'inf-normal'): 0, ('plane', 'nan-normal'): 0,
       ('plane', 'inf-offset'): 0, ('plane', 'nan-offset'): 0}
if len(reference) != 82 or {(f, v) for f, v, _ in reference} != expected | raw.keys():
    raise SystemExit('expected the complete 82-case predicate corpus')
for f, v, valid in reference:
    if (f, v) in raw and int(valid) != raw[f, v]:
        raise SystemExit(f'{f}/{v}: invalid raw-representation oracle verdict')
count = 0
for binary in sys.argv[2:]:
    for family, value, valid in reference + [(f, v, str(int(v not in ['negative', 'inf', 'nan', 'negative-inf'])))
                                           for f in ['shape-fraction', 'world-fraction']
                                           for v in ['zero', 'negative', 'near', 'upper', 'huge', 'inf', 'nan', 'negative-inf']]:
        if (family, value) in raw:
            continue  # Angle input and produced planes: invariants tested in GeometricValues.sx.
        result = subprocess.run([str(Path(binary).resolve()), family, value],
                                capture_output=True, text=True, timeout=10)
        accepted = valid == '1'
        expected_code = 0 if accepted else 1
        diagnostic = 'accepted' if accepted else ('Transform2D requires finite values' if family in ['scalar', 'vector', 'rotation'] else
                      'Ray2D requires finite values' if family.startswith('ray-') else
                      'AABB2D requires finite' if family.startswith('aabb') else
                      'requires finite motion and a non-negative maximum fraction')
        if result.returncode != expected_code or diagnostic not in result.stdout + result.stderr:
            raise SystemExit(f'{family}/{value}: expected {expected_code}, got {result.returncode}\n' + result.stdout + result.stderr)
        count += 1
print(f'geometric values matched {count} public constructor/operation checks; 10 raw representations checked separately')
