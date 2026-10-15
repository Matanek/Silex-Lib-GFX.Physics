#!/usr/bin/env python3
"""Check wheel control settings, inputs and lifetime diagnostics in native modes."""
import os,subprocess
from pathlib import Path
CASES={
    **{n:'requires finite steering angle in [-pi/2, pi/2] and nonnegative representable brake torques' for n in ('angle-low','angle-high','angle-nan','angle-inf','brake-negative','brake-nan','brake-inf','hand-negative','hand-nan','hand-inf','unrepresentable')},
    **{n:'steering axis must be a finite unit vector' for n in ('axis-zero','axis-nan','axis-inf')},
    **{n:'controls require finite steering in [-1, 1] and brakes in [0, 1]' for n in ('steering-low','steering-high','steering-nan','steering-inf','service-low','service-high','service-nan','service-inf','parking-low','parking-high','parking-nan','parking-inf')},
    **{n:'no longer refers to a live vehicle' for n in ('stale','orphan')},
}
def main():
    root=Path.cwd();assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir()
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehicleControls3D.sx';env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-controls-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],check=True,env=env)
            for name,message in CASES.items():
                r=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert r.returncode>0 and message in r.stdout+r.stderr,(name,r)
        finally:binary.unlink(missing_ok=True)
    print(f'vehicle controls rejected {2*len(CASES)} invalid settings, input and lifetime cases')
if __name__=='__main__':main()
