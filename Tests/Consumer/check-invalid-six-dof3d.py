#!/usr/bin/env python3
"""Check cone creation, mutation and lifetime errors through the consumer boundary."""
import os
from pathlib import Path
import subprocess

CASES = {
    'frame': 'requires a finite position and unit rotation',
    'rotation': 'requires a finite position and unit rotation',
    'linear-order': 'bounded requires ordered distinct finite positions',
    'linear-equal': 'bounded requires ordered distinct finite positions',
    'linear-nan': 'bounded requires ordered distinct finite positions',
    'linear-friction': 'requires nonnegative finite friction force',
    'free-spring': 'requires a locked or bounded limit for a spring',
    'spring': 'LinearLimitSpring3D requires positive finite stiffness',
    'linear-speed': 'LinearMotor3D requires finite speed',
    'linear-budget': 'LinearMotor3D requires finite speed and ordered finite force bounds',
    'linear-servo': 'LinearMotor3D.position requires finite position',
    'angular-speed': 'AngularMotor3D requires finite speed',
    'angular-budget': 'AngularMotor3D requires finite speed and nonnegative finite maximum torque',
    'angular-servo': 'AngularMotor3D.position requires an angle',
    'angular-target': 'AngularMotor3D.position requires an angle',
    'angular-friction': 'requires nonnegative finite friction torques',
    'swing': 'cone requires finite half-angles within [0, pi]',
    'twist': 'requires ordered finite twist limits',
    'same': 'requires two distinct bodies',
    'fixed-fixed': 'requires a dynamic body',
    'foreign': 'requires bodies from its world',
    'mutation-anchors': 'requires finite local anchors',
    'mutation-linear': 'bounded requires ordered distinct finite positions',
    'mutation-angular-friction': 'requires nonnegative finite friction torques',
    'mutation-twist': 'requires ordered finite twist limits',
    'stale': 'no longer refers to a live constraint',
    'stale-mutation': 'no longer refers to a live constraint',
    'foreign-destroy': 'cannot destroy a constraint owned by another world',
}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from the workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidSixDOFConstraint3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-six-dof-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '--nocache', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode != 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'six-dof3d rejected {len(CASES) * 2} invalid creation, mutation and lifetime cases')


if __name__ == '__main__':
    main()
