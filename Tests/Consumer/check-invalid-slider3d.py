#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'minimum-nan': 'requires ordered finite position limits',
         'maximum-infinity': 'requires ordered finite position limits',
         'reversed': 'requires ordered finite position limits',
         'mutation-minimum': 'requires ordered finite position limits',
         'mutation-maximum': 'requires ordered finite position limits',
         'mutation-reversed': 'requires ordered finite position limits',
         'position-nan': 'requires a finite position and unit rotation',
         'rotation-zero': 'requires a finite position and unit rotation',
         'mutation-frame': 'requires a finite position and unit rotation',
         'same': 'requires two distinct bodies', 'fixed-kinematic': 'requires a dynamic body',
         'foreign': 'requires bodies from its world', 'stale': 'no longer refers to a live constraint',
         'stale-mutation': 'no longer refers to a live constraint',
         'orphan': 'no longer refers to a live constraint',
         'foreign-destroy': 'cannot destroy a constraint owned by another world'}

for name in ('motor-speed-nan', 'motor-speed-infinity', 'motor-force-nan',
             'motor-force-infinity', 'motor-force-negative'):
    CASES[name] = 'requires finite speed and nonnegative finite maximum force'
for name in ('stale-motor-read', 'stale-motor-set', 'orphan-motor'):
    CASES[name] = 'no longer refers to a live constraint'

for name in ('servo-position-nan', 'servo-position-infinity', 'servo-force-nan', 'servo-force-infinity', 'servo-force-negative', 'servo-stiffness-nan', 'servo-stiffness-infinity', 'servo-stiffness-zero', 'servo-stiffness-negative', 'servo-damping-nan', 'servo-damping-infinity', 'servo-damping-negative'):
    CASES[name] = 'requires finite position, nonnegative finite maximum force, positive finite stiffness and nonnegative finite damping'

for name in ('friction-nan', 'friction-infinity', 'friction-negative', 'mutation-friction-nan', 'mutation-friction-infinity', 'mutation-friction-negative'):
    CASES[name] = 'requires nonnegative finite maximum friction force'
for name in ('stale-friction-read', 'stale-friction-force', 'stale-friction-set', 'orphan-friction'):
    CASES[name] = 'no longer refers to a live constraint'


for name in ('bounds-speed-nan', 'bounds-speed-infinity', 'bounds-minimum-nan', 'bounds-minimum-infinity', 'bounds-maximum-nan', 'bounds-maximum-infinity', 'bounds-ordered'):
    CASES[name] = 'requires finite speed and ordered finite force bounds'
for name in ('bounds-servo-position-nan', 'bounds-servo-position-infinity', 'bounds-servo-minimum-nan', 'bounds-servo-minimum-infinity', 'bounds-servo-maximum-nan', 'bounds-servo-maximum-infinity', 'bounds-servo-stiffness-nan', 'bounds-servo-stiffness-infinity', 'bounds-servo-stiffness-zero', 'bounds-servo-stiffness-negative', 'bounds-servo-damping-nan', 'bounds-servo-damping-infinity', 'bounds-servo-damping-negative', 'bounds-servo-ordered'):
    CASES[name] = 'requires finite position, ordered finite force bounds, positive finite stiffness and nonnegative finite damping'


def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidSliderConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-slider-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'slider3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
