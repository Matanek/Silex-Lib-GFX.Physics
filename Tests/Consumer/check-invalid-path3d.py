#!/usr/bin/env python3
"""Check path creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {'projection-overflow':'requires finite projection', 'closed-distance':'requires a representable distance', 'knot-position': 'requires finite geometry', 'knot-tangent': 'requires finite geometry', 'knot-normal': 'requires a normal independent', 'empty': 'requires two open', 'one': 'requires two open', 'closed-two': 'requires two open', 'cusp': 'requires a regular tangent', 'normal-collapse': 'requires a regular tangent', 'overflow': 'requires finite', 'frame': 'requires a finite distance', 'query': 'requires a finite point', 'hint': 'requires a finite point', 'anchor': 'requires a finite anchor', 'friction-negative': 'requires a finite anchor', 'friction-nan': 'requires a finite anchor', 'mutation-anchor': 'requires a finite anchor', 'mutation-friction': 'requires a finite anchor', 'same': 'requires two distinct bodies', 'fixed-fixed': 'requires a dynamic body', 'foreign': 'requires bodies from its world', 'stale': 'no longer refers to a live constraint', 'stale-mutation': 'no longer refers to a live constraint', 'foreign-destroy': 'cannot destroy a constraint owned by another world'}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidPathConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-path-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'path3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
