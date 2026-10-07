#!/usr/bin/env python3
"""Check creation, mutation and lifetime guards through the public package boundary."""
import os
from pathlib import Path
import subprocess

CASES = {name:"position_and_velocity requires" for name in ('angle-nan', 'angle-inf', 'angle-low', 'angle-high', 'speed-nan', 'speed-inf', 'symmetric-negative', 'symmetric-nan', 'minimum-nan', 'minimum-inf', 'maximum-nan', 'maximum-inf', 'reversed', 'stiffness-zero', 'stiffness-negative', 'stiffness-nan', 'stiffness-inf', 'damping-negative', 'damping-nan', 'damping-inf')}
CASES.update({"stale":"no longer refers to a live constraint","orphan":"no longer refers to a live constraint"})


def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidHingeCombined3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-combined-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'combined targets rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
