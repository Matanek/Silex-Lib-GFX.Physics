#!/usr/bin/env python3
"""Run from the workspace root or Spec Worktree group."""
import os
import subprocess
from pathlib import Path
consumer = Path(__file__).resolve().parent
binary = Path.cwd() / '.silex/invalid-axial-shapes3d'
env = os.environ.copy()
env.setdefault('ZIG_GLOBAL_CACHE_DIR', str(Path.cwd() / '.silex/zig-global'))
cases = {}
for name, keys in [('Cylinder3D',['radius','height','inf','nan','extent']),
                   ('TaperedCylinder3D',['negative','empty','height','inf','nan','extent']),
                   ('TaperedCapsule3D',['radius','bottom','height','inf','nan','extent'])]:
    prefix = {'Cylinder3D':'cylinder','TaperedCylinder3D':'tapered','TaperedCapsule3D':'capsule'}[name]
    for key in keys: cases[prefix+'-'+key] = name+' requires finite valid radii and half-height'
cases.update(dict.fromkeys(['mass-overflow','mass-underflow'], 'requires a positive symmetric inertia tensor'))
try:
    for mode in ('--debug','--release'):
        subprocess.run(['silex','compile',str(consumer/'Smokes/InvalidAxialShapes3D.sx'),mode,'--nocache','--output',str(binary)],check=True,env=env)
        for case,message in cases.items():
            result = subprocess.run([str(binary),case],capture_output=True,text=True)
            if result.returncode == 0 or message not in result.stdout+result.stderr:
                raise RuntimeError(f'{mode} {case}: {result.returncode} {result.stdout}{result.stderr}')
        print(f'{mode}: {len(cases)} invalid axial shapes rejected')
finally:
    binary.unlink(missing_ok=True)
