#!/usr/bin/env python3
"""Check rejected World3D gravity and iteration budgets from the workspace root."""
import argparse
from pathlib import Path
import subprocess
import tempfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', default='silex')
    parser.add_argument('--mode', choices=('debug', 'release'), required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    if Path.cwd().resolve() != here.parents[3]:
        raise ValueError('run from the workspace or Spec Worktree group root')
    expected = {name: 'GFX.Physics.World3D requires position iterations between 1 and 128'
                for name in ('iterations-zero', 'iterations-negative', 'iterations-large')}
    expected.update({name: 'GFX.Physics.World3D requires velocity iterations between 1 and 128'
                     for name in ('velocity-zero', 'velocity-negative', 'velocity-large')})
    expected['gravity'] = 'GFX.Physics.World3D requires finite gravity'
    with tempfile.TemporaryDirectory(prefix='physics-world3d-invalid-') as directory:
        binary = Path(directory) / 'InvalidWorld3D'
        subprocess.run([args.compiler, 'compile', str(here/'Smokes/InvalidWorld3D.sx'),
                        '--backend', 'native', '--'+args.mode, '-o', str(binary)], check=True)
        for name, diagnostic in expected.items():
            result = subprocess.run([str(binary), name], capture_output=True, text=True, timeout=30)
            if result.returncode != 1 or diagnostic not in result.stdout+result.stderr:
                raise AssertionError((name, result.returncode, result.stdout, result.stderr))
            print(name+': rejected with the expected diagnostic')
    print('7 invalid World3D configurations rejected')


if __name__ == '__main__':
    main()
