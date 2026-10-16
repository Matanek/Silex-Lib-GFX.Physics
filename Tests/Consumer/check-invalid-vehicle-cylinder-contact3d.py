#!/usr/bin/env python3
"""Require cylinder wheel calibration diagnostics in both native modes."""
import os
import subprocess
from pathlib import Path

CASES=('zero','negative','nan','infinite','overflow','underflow','radius-underflow','travel-underflow')


def main():
    root=Path.cwd()
    assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir(), 'run from workspace or Spec group root'
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehicleCylinderContact3D.sx'
    env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-cylinder-contact-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],env=env,check=True)
            for name in CASES:
                result=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert result.returncode>0 and 'cylinder contact requires positive representable width, radius and travel' in result.stdout+result.stderr,(name,result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'vehicle cylinder contact rejected {2*len(CASES)} invalid calibration cases')


if __name__=='__main__': main()
