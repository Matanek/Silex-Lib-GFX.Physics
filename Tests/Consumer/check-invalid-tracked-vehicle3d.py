#!/usr/bin/env python3
"""Exercise tracked-vehicle parameter, topology, ownership and lifetime errors."""
import json
import os
from pathlib import Path
import subprocess

CASES = {'band-inertia-0': 'positive representable inertia/ratio', 'band-inertia-1': 'positive representable inertia/ratio', 'band-inertia-2': 'positive representable inertia/ratio', 'band-inertia-3': 'positive representable inertia/ratio', 'band-angular_damping-4': 'positive representable inertia/ratio', 'band-angular_damping-5': 'positive representable inertia/ratio', 'band-maximum_brake_torque-6': 'positive representable inertia/ratio', 'band-maximum_brake_torque-7': 'positive representable inertia/ratio', 'band-differential_ratio-8': 'positive representable inertia/ratio', 'band-differential_ratio-9': 'positive representable inertia/ratio', 'band-empty': 'nonempty wheel indices', 'band-negative': 'driven wheel', 'band-absent-driven': 'driven wheel must belong', 'band-duplicate': 'indices must be distinct', 'band-negative-wheel': 'wheel index must be nonnegative', 'wheel-longitudinal_friction-15': 'nonnegative finite friction', 'wheel-lateral_friction-16': 'nonnegative finite friction', 'wheel-radius-17': 'positive radius', 'wheel-radius-18': 'positive radius', 'wheel-maximum_length-19': 'ordered nonnegative', 'wheel-maximum_slope_angle-20': 'slope angle', 'wheel-forward-21': 'finite unit nonparallel', 'wheel-up-22': 'finite unit nonparallel', 'config-overlap': 'exactly one track', 'config-hole': 'every wheel must belong', 'config-high': 'wheel index is out of range', 'config-driven-high': 'driven wheel index is out of range', 'config-inertia-sum': 'combined track inertia', 'config-ratio-underflow': 'drive ratios and torques', 'config-radius-underflow': 'wheel radii and track inertia', 'config-fixed': 'dynamic chassis', 'config-automatic-rpm': 'shift RPM exceeds engine', 'control-throttle-32': 'requires throttle/track ratios', 'control-throttle-33': 'requires throttle/track ratios', 'control-left_ratio-34': 'requires throttle/track ratios', 'control-right_ratio-35': 'requires throttle/track ratios', 'control-left_ratio-36': 'requires throttle/track ratios', 'control-right_ratio-37': 'requires throttle/track ratios', 'control-right_ratio-38': 'requires throttle/track ratios', 'control-brake-39': 'requires throttle/track ratios', 'control-brake-40': 'requires throttle/track ratios', 'control-brake-41': 'requires throttle/track ratios', 'control-product-underflow': 'ratio products must be representable', 'control-speed-overflow': 'speed limits must be representable', 'gear-high': 'gear is out of range', 'gear-low': 'gear is out of range', 'clutch-low': 'clutch must be finite', 'clutch-high': 'clutch must be finite', 'clutch-nan': 'clutch must be finite', 'automatic-manual': 'requires manual transmission', 'speed-nan': 'angular velocity must be finite and representable', 'speed-infinite': 'angular velocity must be finite and representable', 'speed-overflow': 'angular velocity must be finite and representable', 'wheel-negative': 'wheel index is out of range', 'wheel-high': 'wheel index is out of range', 'wheel-settings': 'wheel index is out of range', 'track-wheel-negative': 'wheel index is out of range', 'track-wheel-high': 'wheel index is out of range', 'tilt-low': 'maximum tilt angle', 'tilt-nan': 'maximum tilt angle', 'expired-chassis': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-wheel': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-wheel-count': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-wheel-settings': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-track': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-track-settings': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-state': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-controls': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-transmission': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-speed': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-tilt': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-set-tilt': 'TrackedVehicle3D no longer refers to a live vehicle', 'expired-double-destroy': 'TrackedVehicle3D no longer refers to a live vehicle', 'orphan-state': 'TrackedVehicle3D no longer refers to a live vehicle', 'foreign-world': 'owned by another world'}

def main():
    root = Path.cwd()
    assert (root/'Silex').is_dir() and (root/'Packages').is_dir()
    entry = Path(__file__).resolve().parent/'Smokes/InvalidTrackedVehicle3D.sx'
    env = os.environ.copy()
    env['ZIG_GLOBAL_CACHE_DIR'] = str(root/'.silex/zig')
    modes = {}
    for mode in ('debug', 'release'):
        binary = root/f'.silex/invalid-tracked-vehicle-{mode}'
        try:
            subprocess.run(['silex', 'compile', str(entry), '--'+mode, '-o', str(binary)], check=True, env=env)
            baseline = subprocess.run([str(binary)], capture_output=True, text=True)
            assert baseline.returncode == 0 and 'baseline valid' in baseline.stdout, baseline
            for name, message in CASES.items():
                result = subprocess.run([str(binary), name], capture_output=True, text=True)
                assert result.returncode > 0 and message in result.stdout+result.stderr, (name, result)
            modes[mode] = len(CASES)
            print(mode, len(CASES), 'invalid tracked vehicle cases rejected', flush=True)
        finally:
            binary.unlink(missing_ok=True)
    print(json.dumps(modes), flush=True)

if __name__ == '__main__':
    main()
