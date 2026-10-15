#!/usr/bin/env python3
"""Require vehicle diagnostics and reject signal termination in both native modes."""
import os
import subprocess
from pathlib import Path

CASES={
    **{name:'finite position and unit suspension direction' for name in ('position','direction')},
    **{name:'positive radius and ordered nonnegative finite suspension lengths' for name in ('radius','radius-nan','minimum','maximum','length-infinite')},
    **{name:'positive finite stiffness and nonnegative finite damping' for name in ('stiffness','damping','stiffness-nan')},
    **{name:'slope angle must be finite' for name in ('slope','slope-nan')},
    **{name:'requires a dynamic chassis' for name in ('fixed','kinematic')},
    'empty':'requires at least one wheel',
    **{name:'wheel index is out of range' for name in ('wheel-index','settings-index','config-index')},
    'foreign':'cannot destroy a vehicle owned by another world',
    **{name:'no longer refers to a live vehicle' for name in ('stale-chassis','stale-wheel','double-destroy','orphan')},
}

def main():
    root=Path.cwd()
    assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir(), 'run from workspace or Spec group root'
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehicle3D.sx'
    env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],env=env,check=True)
            for name,expected in CASES.items():
                result=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert result.returncode>0 and expected in result.stdout+result.stderr,(name,result)
        finally:
            binary.unlink(missing_ok=True)
    print(f'vehicle3d rejected {2*len(CASES)} invalid settings, provenance and lifetime cases')

if __name__=='__main__': main()
