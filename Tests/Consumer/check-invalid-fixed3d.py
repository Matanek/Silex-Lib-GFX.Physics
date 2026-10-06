#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'position-nan': 'requires a finite position and unit rotation',
         'rotation-zero': 'requires a finite position and unit rotation',
         'mutation-frame': 'requires a finite position and unit rotation',
         'same': 'requires two distinct bodies', 'fixed-kinematic': 'requires a dynamic body',
         'foreign': 'requires bodies from its world', 'stale': 'no longer refers to a live constraint',
         'stale-mutation': 'no longer refers to a live constraint',
         'orphan': 'no longer refers to a live constraint',
         'foreign-destroy': 'cannot destroy a constraint owned by another world'}


def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidFixedConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-fixed-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'fixed3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
