#!/usr/bin/env python3
"""Check ragdoll diagnostics and reject signal termination in both native modes."""
import os
from pathlib import Path
import subprocess

CASES = {
    **{name: 'kinematic pose requires one transform per part' for name in ('move-count', 'move-local-count')},
    **{name: 'kinematic duration must be finite and positive' for name in ('move-zero','move-negative','move-nan','move-infinite')},
    'move-overflow': 'kinematic target exceeds finite velocity',
    'move-fixed': 'kinematic pose cannot move a fixed part',
    **{name: 'no longer refers to a live assembly' for name in ('stale-move','stale-resume')},
    'empty': 'requires at least one part',
    **{name: 'requires one root followed by children after their parent'
       for name in ('root-parent', 'second-root', 'future-parent', 'missing-parent')},
    'body-transform': 'places bodies through body_offset',
    'joint-frame': 'derives joint frames from the rest pose',
    'density': 'requires finite motion, density, damping and sleep threshold',
    'limits': 'requires ordered finite twist limits',
    'fixed-pair': 'requires a dynamic body at every joint',
    **{name: 'pose requires one transform per part' for name in ('pose-count', 'local-count')},
    **{name: 'part index is out of range' for name in ('body-index', 'joint-index', 'settings-index')},
    **{name: 'motor pose requires one transform per part' for name in ('drive-count', 'drive-local-count')},
    **{name: 'positive finite stiffness and nonnegative finite damping' for name in
       ('motor-torque', 'motor-stiffness', 'motor-damping', 'motor-torque-nan', 'motor-stiffness-nan', 'motor-damping-nan', 'motor-root-only')},
    **{name: 'no longer refers to a live assembly' for name in ('stale-drive', 'stale-stop')},
    'foreign-destroy': 'cannot destroy a ragdoll owned by another world',
    'double-destroy': 'was already destroyed',
    **{name: 'no longer refers to a live assembly' for name in ('stale-read', 'stale-pose', 'orphan-read')},
}

def main():
    root = Path.cwd()
    assert (root / 'Packages').is_dir() and (root / 'Silex-Examples').is_dir(), 'run from workspace or Spec group root'
    source = Path(__file__).resolve().parent / 'Smokes/InvalidRagdoll3D.sx'
    environment = os.environ.copy()
    environment['ZIG_GLOBAL_CACHE_DIR'] = str(root / '.silex/zig')
    for mode in ('debug', 'release'):
        binary = root / f'.silex/invalid-ragdoll-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(source), f'--{mode}', '-o', str(binary)],
                           env=environment, check=True)
            for name, expected in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode > 0 and expected in result.stdout + result.stderr, (name, result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'ragdoll3d rejected {len(CASES) * 2} invalid hierarchy, pose and lifetime cases')

if __name__ == '__main__':
    main()
