#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {name:'ordered finite torque bounds' for name in (
    'speed-nan','speed-inf','minimum-nan','maximum-nan','minimum-inf','maximum-inf','reversed')}
CASES.update({name:'requires an angle within [-pi, pi]' for name in (
    'position-minimum-nan','position-maximum-inf','position-reversed','position-angle','position-stiffness','position-damping')})
CASES.update({'stale':'no longer refers to a live constraint','orphan':'no longer refers to a live constraint'})


def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidHingeTorqueBounds3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-torque-bounds-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'torque bounds rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
