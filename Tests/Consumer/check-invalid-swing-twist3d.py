#!/usr/bin/env python3
"""Check cone creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {
    'frame': 'requires a finite position and unit rotation',
    'rotation': 'requires a finite position and unit rotation',
    'cone-negative': 'cone requires finite half-angles within [0, pi]',
    'cone-range': 'cone requires finite half-angles within [0, pi]',
    'cone-nan': 'cone requires finite half-angles within [0, pi]',
    'pyramid-order': 'pyramid requires ordered finite angles',
    'pyramid-nan': 'pyramid requires ordered finite angles',
    'twist-order': 'requires ordered finite twist limits',
    'twist-range': 'requires ordered finite twist limits',
    'friction': 'requires nonnegative finite friction torque',
    'twist-speed': 'TwistMotor3D requires finite speed',
    'twist-budget': 'TwistMotor3D requires finite speed and ordered finite torque bounds',
    'twist-servo': 'TwistMotor3D.position requires an angle',
    'swing-speed': 'SwingMotor3D requires finite speed',
    'swing-budget': 'SwingMotor3D requires finite speed and nonnegative finite maximum torque',
    'swing-servo': 'SwingMotor3D.position requires an angle',
    'same': 'requires two distinct bodies',
    'fixed-fixed': 'requires a dynamic body',
    'foreign': 'requires bodies from its world',
    'mutation-anchors': 'requires finite local anchors',
    'mutation-swing': 'cone requires finite half-angles within [0, pi]',
    'mutation-twist': 'requires ordered finite twist limits',
    'mutation-friction': 'requires nonnegative finite friction torque',
    'stale': 'no longer refers to a live constraint',
    'stale-mutation': 'no longer refers to a live constraint',
    'foreign-destroy': 'cannot destroy a constraint owned by another world',
}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidSwingTwistConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-swing-twist-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'swing-twist3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
