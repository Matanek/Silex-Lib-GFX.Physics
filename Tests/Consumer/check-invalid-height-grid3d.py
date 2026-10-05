#!/usr/bin/env python3
"""Run from the workspace root or Spec Worktree group."""
import os
import subprocess
from pathlib import Path
consumer = Path(__file__).resolve().parent
binary = Path.cwd() / '.silex/invalid-height-grid3d'
env = os.environ.copy()
env.setdefault('ZIG_GLOBAL_CACHE_DIR', str(Path.cwd() / '.silex/zig-global'))
cases = dict.fromkeys(['columns','rows','count'], 'height grid requires at least two samples per axis and one height per vertex')
cases['spacing'] = 'height grid requires positive finite spacing'
cases['height'] = 'height grid requires finite heights'
cases['mask'] = 'height grid requires an empty hole mask or one flag per vertex'
cases['empty'] = 'height grid requires at least one unmasked triangle'

try:
    for mode in ('--debug','--release'):
        subprocess.run(['silex','compile',str(consumer/'Smokes/InvalidHeightGrid3D.sx'),mode,'--nocache','--output',str(binary)],check=True,env=env)
        for case,message in cases.items():
            result = subprocess.run([str(binary),case],capture_output=True,text=True)
            if result.returncode == 0 or message not in result.stdout+result.stderr:
                raise RuntimeError(f'{mode} {case}: {result.returncode} {result.stdout}{result.stderr}')
        print(f'{mode}: {len(cases)} invalid height grids rejected')
finally:
    binary.unlink(missing_ok=True)
