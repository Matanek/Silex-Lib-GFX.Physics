#!/usr/bin/env python3
"""Run from the workspace root or the Spec Worktree group."""
import os
import subprocess
from pathlib import Path
consumer = Path(__file__).resolve().parent
binary = Path.cwd() / '.silex/invalid-sphere-cast3d'
env = os.environ.copy()
env.setdefault('ZIG_GLOBAL_CACHE_DIR', str(Path.cwd() / '.silex/zig-global'))
cases = dict.fromkeys(['zero', 'origin', 'translation', 'squared', 'nan'], 'requires a finite origin, endpoint and nonzero finite translation')
cases['radius'] = 'requires a finite positive radius'
try:
    for mode in ('--debug', '--release'):
        subprocess.run(['silex', 'compile', str(consumer/'Smokes/InvalidSphereCast3D.sx'), mode, '--nocache', '--output', str(binary)], check=True, env=env)
        for case, message in cases.items():
            result = subprocess.run([str(binary), case], text=True, capture_output=True)
            if result.returncode == 0 or message not in result.stdout + result.stderr:
                raise RuntimeError(f'{mode} {case}: code={result.returncode}, {result.stdout}{result.stderr}')
        print(f'{mode}: {len(cases)} invalid sphere casts rejected')
finally:
    binary.unlink(missing_ok=True)
