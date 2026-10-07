#!/usr/bin/env python3
"""Check pulley creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'world-anchor': 'requires finite anchors', 'local-anchor': 'requires finite anchors', 'mutation-local': 'requires finite anchors', 'mutation-world': 'requires finite anchors', 'geometry-overflow': 'requires finite cable geometry', 'mutation-local-geometry': 'requires finite cable geometry', 'mutation-world-geometry': 'requires finite cable geometry', 'ratio-zero': 'requires a finite positive representable ratio', 'ratio-negative': 'requires a finite positive representable ratio', 'ratio-nan': 'requires a finite positive representable ratio', 'ratio-overflow': 'requires a finite positive representable ratio', 'ratio-underflow': 'requires a finite positive representable ratio', 'mutation-ratio': 'requires a finite positive representable ratio', 'minimum-negative': 'requires finite ordered nonnegative lengths', 'minimum-nan': 'requires finite ordered nonnegative lengths', 'maximum-negative': 'requires finite ordered nonnegative lengths', 'maximum-nan': 'requires finite ordered nonnegative lengths', 'limits-inverted': 'requires finite ordered nonnegative lengths', 'automatic-inverted': 'requires finite ordered nonnegative lengths', 'mutation-limits': 'requires finite ordered nonnegative lengths', 'same': 'requires two distinct bodies', 'fixed-fixed': 'requires a dynamic body', 'foreign': 'requires bodies from its world', 'stale': 'no longer refers to a live constraint', 'stale-mutation': 'no longer refers to a live constraint', 'foreign-destroy': 'cannot destroy a constraint owned by another world'}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidPulleyConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-pulley-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'pulley3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
