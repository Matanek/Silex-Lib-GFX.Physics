#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'anchor': 'requires finite local anchors', 'axis-zero': 'requires finite nonzero axes',
         'axis-nan': 'requires finite nonzero axes', 'collinear': 'requires a normal independent',
         'limits-order': 'requires ordered finite angles', 'limits-range': 'requires ordered finite angles',
         'limits-nan': 'requires ordered finite angles', 'same': 'requires two distinct bodies',
         'fixed-fixed': 'requires a dynamic body', 'foreign': 'requires bodies from its world',
         'mutation-anchors': 'requires finite local anchors', 'mutation-frames': 'requires finite nonzero axes',
         'mutation-limits': 'requires ordered finite angles', 'stale': 'no longer refers to a live constraint',
         'foreign-destroy': 'cannot destroy a constraint owned by another world'}


def main():
    root = Path.cwd()
    source = Path(__file__).resolve().parent / 'Smokes/InvalidHingeConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-hinge-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'hinge3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
