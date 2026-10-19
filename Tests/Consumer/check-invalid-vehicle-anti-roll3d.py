#!/usr/bin/env python3
"""Require public anti-roll calibration diagnostics in both native modes."""
import os
import subprocess
from pathlib import Path
CASES={**dict.fromkeys(('left-negative','right-negative','same-wheel'),'requires distinct nonnegative wheel indices'),**dict.fromkeys(('negative','nan','infinite'),'requires nonnegative finite stiffness'),'out-of-range':'anti-roll wheel index is out of range','overlap':'anti-roll bars require disjoint wheel pairs','overflow':'anti-roll stiffness and travel must be representable',**dict.fromkeys(('read-negative','read-high'),'anti-roll bar index is out of range')}
def main():
    root=Path.cwd();assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir(),'run from workspace or Spec group root'
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehicleAntiRoll3D.sx';env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-anti-roll-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],env=env,check=True)
            for name,diagnostic in CASES.items():
                result=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert result.returncode>0 and diagnostic in result.stdout+result.stderr,(name,result)
        finally:binary.unlink(missing_ok=True)
    print(f'vehicle anti-roll rejected {2*len(CASES)} invalid calibration cases')
if __name__=='__main__':main()
