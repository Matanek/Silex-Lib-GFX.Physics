#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {name:'requires nonnegative finite maximum friction torque' for name in (
    'create-negative','create-nan','mutate-negative','mutate-nan')}
CASES.update({name:'no longer refers to a live constraint' for name in (
    'stale-read','stale-write','orphan-read','orphan-write')})


def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidHingeFriction3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-friction-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'friction3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
