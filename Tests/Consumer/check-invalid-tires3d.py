#!/usr/bin/env python3
"""Check public tire diagnostics in both native build modes."""
import os, subprocess
from pathlib import Path
CASES={
    'empty':'requires at least one point',
    **{name:'requires ordered nonnegative finite slips and coefficients' for name in ('negative-x','negative-y','duplicate','unordered','nan-point','infinite-point')},
    **{name:'slip must be finite and nonnegative' for name in ('negative-slip','nan-slip','infinite-slip')},
    **{name:'requires positive finite inertia and nonnegative finite angular damping' for name in ('inertia','nan-inertia','infinite-inertia','damping','nan-damping','infinite-damping')},
    **{name:'requires finite unit nonparallel forward and up vectors' for name in ('forward','nan-forward','parallel','up')},
    'no-tire':'wheel requires a tire to rotate','index':'wheel index is out of range',
    **{name:'no longer refers to a live vehicle' for name in ('stale','orphan')},
    **{name:'wheel angular velocity must be finite and representable' for name in ('nan-spin','infinite-spin','large-spin')},
}
def main():
    root=Path.cwd();assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir()
    source=Path(__file__).resolve().parent/'Smokes/InvalidTires3D.sx';env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-tires-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],check=True,env=env)
            for name,message in CASES.items():
                r=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert r.returncode>0 and message in r.stdout+r.stderr,(name,r)
        finally:binary.unlink(missing_ok=True)
    print(f'tires3d rejected {2*len(CASES)} invalid settings, curve, spin and lifetime cases')
if __name__=='__main__':main()
