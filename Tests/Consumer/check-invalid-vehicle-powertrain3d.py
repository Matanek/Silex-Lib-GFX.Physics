#!/usr/bin/env python3
"""Check powertrain settings, inputs and lifetime diagnostics in native modes."""
import os,subprocess
from pathlib import Path
CASES={'engine-maximum_torque-negative': 'requires finite ordered RPM bounds',
 'engine-minimum_rpm-negative': 'requires finite ordered RPM bounds',
 'engine-angular_damping-negative': 'requires finite ordered RPM bounds',
 'engine-maximum_torque-nan': 'requires finite ordered RPM bounds',
 'engine-minimum_rpm-nan': 'requires finite ordered RPM bounds',
 'engine-angular_damping-nan': 'requires finite ordered RPM bounds',
 'engine-maximum_torque-inf': 'requires finite ordered RPM bounds',
 'engine-minimum_rpm-inf': 'requires finite ordered RPM bounds',
 'engine-angular_damping-inf': 'requires finite ordered RPM bounds',
 'engine-inertia-9': 'requires finite ordered RPM bounds',
 'engine-inertia-10': 'requires finite ordered RPM bounds',
 'engine-maximum_rpm-11': 'requires finite ordered RPM bounds',
 'engine-maximum_rpm-12': 'requires finite ordered RPM bounds',
 'curve-empty': 'requires a torque curve',
 'curve-order': 'torque curve requires ordered RPM fractions',
 'curve-x-low': 'torque curve requires ordered RPM fractions',
 'curve-x-high': 'torque curve requires ordered RPM fractions',
 'curve-y-low': 'torque curve requires ordered RPM fractions',
 'curve-y-high': 'torque curve requires ordered RPM fractions',
 'curve-nan': 'torque curve requires ordered RPM fractions',
 'trans-forward-empty': 'requires forward and reverse ratios',
 'trans-reverse-empty': 'requires forward and reverse ratios',
 'trans-forward-zero': 'ratios must be',
 'trans-forward-negative': 'ratios must be',
 'trans-forward-inf': 'ratios must be',
 'trans-reverse-positive': 'ratios must be',
 'trans-reverse-nan': 'ratios must be',
 'trans-clutch-torque-negative': 'clutch torque limit must be finite and nonnegative',
 'trans-clutch-torque-nan': 'clutch torque limit must be finite and nonnegative',
 'trans-clutch-torque-inf': 'clutch torque limit must be finite and nonnegative',
 'trans-clutch_strength': 'requires finite nonnegative clutch/times',
 'trans-switch_time': 'requires finite nonnegative clutch/times',
 'trans-clutch_release_time': 'requires finite nonnegative clutch/times',
 'trans-switch_latency': 'requires finite nonnegative clutch/times',
 'trans-shift_down_rpm': 'requires finite nonnegative clutch/times',
 'trans-shift_up_rpm': 'requires finite nonnegative clutch/times',
 'diff-none': 'requires one or two distinct wheel indices',
 'diff-duplicate': 'requires one or two distinct wheel indices',
 'diff-index-low': 'requires one or two distinct wheel indices',
 'diff-ratio-36': 'requires finite positive ratio',
 'diff-ratio-37': 'requires finite positive ratio',
 'diff-left_right_split-38': 'requires finite positive ratio',
 'diff-left_right_split-39': 'requires finite positive ratio',
 'diff-engine_torque_ratio-40': 'requires finite positive ratio',
 'diff-limit-41': 'limited slip ratio must be',
 'diff-limit-42': 'limited slip ratio must be',
 'diff-limit-43': 'limited slip ratio must be',
 'engine-no-diff': 'engine requires differentials with total torque share one',
 'diff-no-engine': 'differentials require an engine',
 'diff-out-of-range': 'differential wheel index is out of range',
 'diff-without-tire': 'driven wheels require tires',
 'diff-reused-wheel': 'driven wheels must belong to one differential',
 'diff-wrong-total': 'engine requires differentials with total torque share one',
 'center-limit': 'limited slip ratio must be',
 'throttle-low': 'throttle must be finite in [-1, 1]',
 'throttle-high': 'throttle must be finite in [-1, 1]',
 'throttle-nan': 'throttle must be finite in [-1, 1]',
 'throttle-inf': 'throttle must be finite in [-1, 1]',
 'throttle-no-engine': 'throttle requires an engine',
 'automatic-manual-input': 'requires manual transmission',
 'gear-100': 'gear is out of range',
 'gear--100': 'gear is out of range',
 'clutch-low': 'clutch must be finite in [0, 1]',
 'clutch-high': 'clutch must be finite in [0, 1]',
 'clutch-nan': 'clutch must be finite in [0, 1]',
 'stale-transmission': 'no longer refers to a live vehicle',
 'stale-state': 'no longer refers to a live vehicle',
 'orphan-state': 'no longer refers to a live vehicle',
 'no-engine-state': 'has no engine',
 'no-engine-transmission': 'has no engine'}

def main():
    root=Path.cwd();assert (root/'Packages').is_dir() and (root/'Silex-Examples').is_dir()
    source=Path(__file__).resolve().parent/'Smokes/InvalidVehiclePowertrain3D.sx';env=os.environ.copy();env['ZIG_GLOBAL_CACHE_DIR']=str(root/'.silex/zig')
    for mode in ('debug','release'):
        binary=root/f'.silex/invalid-vehicle-powertrain-{mode}'
        try:
            subprocess.run(['silex','compile',str(source),'--'+mode,'-o',str(binary)],check=True,env=env)
            for name,message in CASES.items():
                r=subprocess.run([str(binary),name],capture_output=True,text=True)
                assert r.returncode>0 and message in r.stdout+r.stderr,(name,r)
        finally:binary.unlink(missing_ok=True)
    print(f'vehicle powertrain rejected {2*len(CASES)} invalid settings, input and lifetime cases')
if __name__=='__main__':main()
