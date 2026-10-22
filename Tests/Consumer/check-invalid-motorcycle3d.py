#!/usr/bin/env python3
"""Check motorcycle gains, wheel configuration, control and handle diagnostics."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

CASES = {'lean-negative': 'maximum lean angle', 'lean-half-pi': 'maximum lean angle', 'lean-pi': 'maximum lean angle', 'lean-nan': 'maximum lean angle', 'lean-infinite': 'maximum lean angle', 'stiffness-negative': 'nonnegative finite representable gains', 'stiffness-nan': 'nonnegative finite representable gains', 'stiffness-infinite': 'nonnegative finite representable gains', 'stiffness-overflow': 'nonnegative finite representable gains', 'damping-negative': 'nonnegative finite representable gains', 'damping-nan': 'nonnegative finite representable gains', 'damping-infinite': 'nonnegative finite representable gains', 'damping-overflow': 'nonnegative finite representable gains', 'integral_gain-negative': 'nonnegative finite representable gains', 'integral_gain-nan': 'nonnegative finite representable gains', 'integral_gain-infinite': 'nonnegative finite representable gains', 'integral_gain-overflow': 'nonnegative finite representable gains', 'integral_decay-negative': 'nonnegative finite representable gains', 'integral_decay-nan': 'nonnegative finite representable gains', 'integral_decay-infinite': 'nonnegative finite representable gains', 'integral_decay-overflow': 'nonnegative finite representable gains', 'smoothing-negative': 'smoothing must be finite', 'smoothing-high': 'smoothing must be finite', 'smoothing-nan': 'smoothing must be finite', 'smoothing-infinite': 'smoothing must be finite', 'fixed': 'dynamic chassis', 'kinematic': 'dynamic chassis', 'front-tire': 'tires on both wheels', 'rear-tire': 'tires on both wheels', 'span-zero': 'positive representable wheelbase', 'span-negative': 'positive representable wheelbase', 'span-overflow': 'positive representable wheelbase', 'span-underflow': 'positive representable wheelbase', 'up-zero': 'orthogonal unit up and forward', 'up-length': 'orthogonal unit up and forward', 'up-nan': 'orthogonal unit up and forward', 'forward-zero': 'orthogonal unit up and forward', 'forward-length': 'orthogonal unit up and forward', 'forward-parallel': 'orthogonal unit up and forward', 'forward-nan': 'orthogonal unit up and forward', 'ratio-zero': 'positive finite representable drive ratio', 'ratio-negative': 'positive finite representable drive ratio', 'ratio-nan': 'positive finite representable drive ratio', 'ratio-infinite': 'positive finite representable drive ratio', 'ratio-overflow': 'positive finite representable drive ratio', 'steering-high': 'finite steering', 'steering-nan': 'finite steering', 'brake-low': 'brakes in [0, 1]', 'brake-high': 'brakes in [0, 1]', 'handbrake-high': 'brakes in [0, 1]', 'throttle-high': 'throttle must be finite', 'throttle-nan': 'throttle must be finite', 'throttle-unpowered': 'throttle requires an engine', 'state-unpowered': 'has no engine', 'gear-unpowered': 'has no engine', 'wheel-low': 'wheel index is out of range', 'wheel-high': 'wheel index is out of range', 'wheel-settings-high': 'wheel index is out of range', 'wheel-speed-nan': 'angular velocity must be finite', 'wheel-speed-infinite': 'angular velocity must be finite', 'wheel-speed-overflow': 'angular velocity must be finite', 'tilt-negative': 'maximum tilt angle', 'tilt-nan': 'maximum tilt angle', 'expired-chassis': 'no longer refers to a live vehicle', 'expired-wheel': 'no longer refers to a live vehicle', 'expired-wheel-count': 'no longer refers to a live vehicle', 'expired-wheel-settings': 'no longer refers to a live vehicle', 'expired-powertrain': 'no longer refers to a live vehicle', 'expired-controls': 'no longer refers to a live vehicle', 'expired-transmission': 'no longer refers to a live vehicle', 'expired-speed': 'no longer refers to a live vehicle', 'expired-tilt': 'no longer refers to a live vehicle', 'expired-set-tilt': 'no longer refers to a live vehicle', 'expired-balance': 'no longer refers to a live vehicle', 'expired-set-balance': 'no longer refers to a live vehicle', 'expired-balance-enabled': 'no longer refers to a live vehicle', 'expired-set-balance-enabled': 'no longer refers to a live vehicle', 'expired-steering-limit': 'no longer refers to a live vehicle', 'expired-set-steering-limit': 'no longer refers to a live vehicle', 'expired-target': 'no longer refers to a live vehicle', 'expired-double-destroy': 'no longer refers to a live vehicle', 'orphan': 'no longer refers to a live vehicle', 'foreign': 'owned by another world'}

def main():
    root=Path.cwd()
    if not (root/'Silex').is_dir() or not (root/'Packages').is_dir():
        raise ValueError('run from workspace or Spec group root')
    entry=Path(__file__).resolve().parent/'Smokes/InvalidMotorcycle3D.sx'
    env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    report={}
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-motorcycle-{mode}'
        command=['silex','compile',str(entry),'--'+mode,'--output',str(binary)]
        subprocess.run(command,check=True,env=env)
        baseline=subprocess.run([str(binary)],capture_output=True,text=True)
        assert baseline.returncode==0 and 'baseline valid' in baseline.stdout,baseline
        results={}
        for name,message in CASES.items():
            result=subprocess.run([str(binary),name],capture_output=True,text=True)
            output=result.stdout+result.stderr
            assert result.returncode>0 and message in output,(name,result)
            results[name]=dict(exit_code=result.returncode,diagnostic=output)
        report[mode]=dict(command=command,source_sha256=hashlib.sha256(entry.read_bytes()).hexdigest(),binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),cases=results)
        (root/'.silex/motorcycle-invalid-qualification.json').write_text(json.dumps(report,indent=2)+'\n')
        print(mode,len(CASES),'invalid motorcycle cases rejected',flush=True)

if __name__=='__main__': main()
