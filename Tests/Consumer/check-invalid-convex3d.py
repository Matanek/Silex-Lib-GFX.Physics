#!/usr/bin/env python3
"""Run from the workspace root or the Spec Worktree group."""
import os
import subprocess
from pathlib import Path

consumer = Path(__file__).resolve().parent
binary = Path.cwd() / '.silex/invalid-convex3d'
env = os.environ.copy()
env.setdefault('ZIG_GLOBAL_CACHE_DIR', str(Path.cwd() / '.silex/zig-global'))
cases = {
    'few': 'requires a solid point cloud',
    'planar': 'requires a non-coplanar solid point cloud',
    'collinear': 'requires a non-coplanar solid point cloud',
    'duplicate': 'requires a finite solid point cloud',
    'finite': 'requires finite points',
    'compound': 'cannot contain a convex hull',
    'triangle-pair': 'unsupported shape pair',
}
try:
    for mode in ('--debug', '--release'):
        subprocess.run(['silex', 'compile', str(consumer/'Smokes/InvalidConvexHull3D.sx'), mode, '--nocache',
                        '--output', str(binary)], check=True, env=env)
        for case, message in cases.items():
            result = subprocess.run([str(binary), case], text=True, capture_output=True)
            if result.returncode == 0 or message not in result.stdout + result.stderr:
                raise RuntimeError(f'{mode} {case}: code={result.returncode}, {result.stdout}{result.stderr}')
        print(f'{mode}: {len(cases)} invalid convex uses rejected')
finally:
    binary.unlink(missing_ok=True)
