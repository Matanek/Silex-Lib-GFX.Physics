#!/usr/bin/env python3
"""Run from the workspace root or Spec Worktree group."""
import os
import subprocess
from pathlib import Path
consumer = Path(__file__).resolve().parent
binary = Path.cwd() / '.silex/invalid-plane3d'
env = os.environ.copy()
env.setdefault('ZIG_GLOBAL_CACHE_DIR', str(Path.cwd() / '.silex/zig-global'))
cases = dict.fromkeys(['zero','normal','offset'],'Plane3D requires a finite nonzero normal and finite offset')
cases.update(dict.fromkeys(['dynamic','kinematic','replace'],'Plane3D requires a fixed body'))
cases['compound'] = 'CompoundChild3D cannot contain a plane'
cases['cast'] = 'ShapeCast3D requires a convex volume primitive or convex hull'
cases['pair'] = 'Geometry3D does not provide plane/plane distance'

try:
    for mode in ('--debug','--release'):
        subprocess.run(['silex','compile',str(consumer/'Smokes/InvalidPlane3D.sx'),mode,'--nocache','--output',str(binary)],check=True,env=env)
        for case,message in cases.items():
            result = subprocess.run([str(binary),case],capture_output=True,text=True)
            if result.returncode == 0 or message not in result.stdout+result.stderr:
                raise RuntimeError(f'{mode} {case}: {result.returncode} {result.stdout}{result.stderr}')
        print(f'{mode}: {len(cases)} invalid planes rejected')
finally:
    binary.unlink(missing_ok=True)
