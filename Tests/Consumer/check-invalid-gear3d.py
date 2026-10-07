#!/usr/bin/env python3
"""Check gear creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'axis-zero': 'requires finite nonzero axes', 'axis-nan': 'requires finite nonzero axes', 'axis-overflow': 'requires finite nonzero axes', 'mutation-axes': 'requires finite nonzero axes', 'ratio-zero': 'requires a finite nonzero representable ratio', 'ratio-nan': 'requires a finite nonzero representable ratio', 'ratio-overflow': 'requires a finite nonzero representable ratio', 'ratio-underflow': 'requires a finite nonzero representable ratio', 'mutation-ratio': 'requires a finite nonzero representable ratio', 'same': 'requires two distinct bodies', 'fixed-fixed': 'requires a dynamic body', 'foreign': 'requires bodies from its world', 'stale': 'no longer refers to a live constraint', 'stale-mutation': 'no longer refers to a live constraint', 'foreign-destroy': 'cannot destroy a constraint owned by another world'}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidGearConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-gear-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'gear3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
