#!/usr/bin/env python3
"""Check cone creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {
    'anchor': 'requires finite local anchors',
    'axis-zero': 'requires finite nonzero axes',
    'axis-nan': 'requires finite nonzero axes',
    'angle-negative': 'requires a finite half-angle within [0, pi]',
    'angle-range': 'requires a finite half-angle within [0, pi]',
    'angle-nan': 'requires a finite half-angle within [0, pi]',
    'same': 'requires two distinct bodies',
    'fixed-fixed': 'requires a dynamic body',
    'foreign': 'requires bodies from its world',
    'mutation-anchors': 'requires finite local anchors',
    'mutation-axes': 'requires finite nonzero axes',
    'mutation-angle': 'requires a finite half-angle within [0, pi]',
    'stale': 'no longer refers to a live constraint',
    'stale-mutation': 'no longer refers to a live constraint',
    'foreign-destroy': 'cannot destroy a constraint owned by another world',
}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidConeConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-cone-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'cone3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
