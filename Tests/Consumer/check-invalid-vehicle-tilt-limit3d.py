#!/usr/bin/env python3
"""Require public vehicle tilt diagnostics in both native modes."""
import os
import subprocess
from pathlib import Path

CASES={**dict.fromkeys(('negative','high','nan','infinite','live-negative','live-high','live-nan','live-infinite'),'requires a finite maximum tilt angle in [0, pi]'),**dict.fromkeys(('up-zero','up-nonunit','up-nan','up-infinite'),'up must be a finite unit vector'),**dict.fromkeys(('expired-read','expired-write'),'no longer refers to a live vehicle')}

def main():
    root=Path.cwd();assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir(),'run from workspace or Spec group root'
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehicleTiltLimit3D.sx';env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-tilt-limit-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],env=env,check=True)
            for name,diagnostic in CASES.items():
                result=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert result.returncode>0 and diagnostic in result.stdout+result.stderr,(name,result)
        finally:binary.unlink(missing_ok=True)
    print(f'vehicle tilt limit rejected {2*len(CASES)} invalid calibration/lifetime cases')
if __name__=='__main__':main()
