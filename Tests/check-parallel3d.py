#!/usr/bin/env python3
"""Qualify native 3D worker correctness before optionally measuring Release cost."""
import argparse
import hashlib
import json
import math
import platform
import re
from pathlib import Path
import statistics
import subprocess
import tempfile
import time


def checked(command, timeout):
    result = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError((command, result.returncode, result.stdout, result.stderr))
    return result.stdout + result.stderr


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiler', default='silex')
    parser.add_argument('--mode', choices=('debug', 'release'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--measure', action='store_true')
    parser.add_argument('--binaries', type=Path, help='reuse these exact precompiled binaries')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    if Path.cwd().resolve() != here.parents[2]:
        raise ValueError('run from SilexProject or the Spec Worktree group root')
    if args.measure and args.mode != 'release':
        raise ValueError('cost measurements require Release')
    sources = {'consumer': here/'Consumer/Tests/ParallelWorld3D.sx',
               'workers': here/'ParallelWorkers3D.sx', 'safety': here/'ParallelSafety3D.sx'}
    report = {'mode': args.mode, 'target': platform.system()+'-'+platform.machine(), 'compiler': checked([args.compiler, '--version'], 10).strip(),
              'sources': {name: digest(path) for name, path in sources.items()},
              'numeric_rule': 'exact equality on the same source/build/target; ordered identities/events/manifold impulses',
              'runs': [], 'cost_fixture': {'seed': 0, 'body_count': 513, 'dynamic_spheres': 256, 'radius_m': 0.2, 'density': 1.0, 'distance_constraints': 256, 'distance_m': 10.0, 'fixed_support': 'shared plane and individual anchors', 'gravity_m_s2': [0.0,-9.81,0.0], 'fixed_step_seconds': 1.0/60.0, 'velocity_iterations': 12, 'position_iterations': 4, 'warmup_steps': 4, 'measured_steps': 32}}
    with tempfile.TemporaryDirectory(prefix='physics-parallel3d-') as temporary:
        directory = args.binaries.resolve() if args.binaries else Path(temporary).resolve()
        binaries = {name: directory/name for name in sources}
        if not args.binaries:
            for name, source in sources.items():
                checked([args.compiler, 'compile', str(source), '--backend', 'native', '--'+args.mode,
                         '-o', str(binaries[name])], 2400)
        report['binaries'] = {name: digest(path) for name, path in binaries.items()}
        for name in ('consumer', 'workers'):
            output = checked([str(binaries[name])], 1200 if name == 'consumer' else 40)
            report['runs'].append({'case': name, 'output': output})
            print(name+': passed', flush=True)
        for case in ('zero', 'negative', 'workers', 'create', 'destroy', 'body', 'step'):
            result = subprocess.run([str(binaries['safety']), case], capture_output=True, text=True, timeout=20)
            expected = 'parallel worker count must be positive' if case in ('zero','negative') else 'cannot be modified during step'
            output = result.stdout+result.stderr
            if result.returncode != 1 or expected not in output:
                raise AssertionError((case, result.returncode, output))
            report['runs'].append({'case': case, 'exit_code': result.returncode, 'output': output})
        if args.measure:
            samples = {'one': [], 'four': []}
            signatures = set()
            raw = []
            # Seven fresh processes per configuration, balanced AB/BA ordering.
            for repetition in range(7):
                order = ('one','four') if repetition%2==0 else ('four','one')
                for workers in order:
                    start = time.monotonic()
                    command = [str(binaries['consumer']), workers]
                    if platform.system() == 'Darwin':
                        command = ['/usr/bin/time', '-l'] + command
                    output = checked(command, 120)
                    lines = output.splitlines()
                    times = [line for line in lines if line.startswith('steps_ms')]
                    states = [line for line in lines if line.startswith('signature')]
                    preparations = [line for line in lines if line.startswith('prepare_ms')]
                    if len(times)!=1 or len(states)!=1 or len(preparations)!=1:
                        raise AssertionError(('missing or duplicate measurement', output))
                    value = float(times[0][len('steps_ms'):].strip())
                    preparation = float(preparations[0][len('prepare_ms'):].strip())
                    if not math.isfinite(preparation) or preparation<0:
                        raise AssertionError(('invalid preparation time', output))
                    if not 0 < value < float('inf'):
                        raise AssertionError(('nonfinite measurement', output))
                    state = re.fullmatch(r'signature\s*(.*?)\s*contacts\s*(\d+)', states[0])
                    if state is None or not math.isfinite(float(state.group(1))) or not 0<=int(state.group(2))<=256:
                        raise AssertionError(('invalid measured state', output))
                    signatures.add(states[0]); samples[workers].append(value)
                    raw.append({'repetition': repetition, 'workers': workers, 'steps_ms': value, 'preparation_ms': preparation,
                                'process_seconds': time.monotonic()-start, 'output': output,
                                'peak_resident_bytes': int(re.search(r'(?m)^\s*(\d+)\s+maximum resident set size', output).group(1)) if platform.system()=='Darwin' else None})
            if len(signatures)!=1:
                raise AssertionError(('unstable measured state', signatures))
            report['measurements'] = raw
            report['statistics'] = {}
            for workers, values in samples.items():
                median = statistics.median(values)
                mad = statistics.median(abs(value-median) for value in values)
                report['statistics'][workers] = {'median_ms': median, 'minimum_ms': min(values),
                    'maximum_ms': max(values), 'mad_ms': mad, 'mad_percent': mad/median*100}
            report['performance_conclusion_allowed'] = all(value['mad_percent']<=5 for value in report['statistics'].values())
            for workers in samples:
                preparation = [row['preparation_ms'] for row in raw if row['workers']==workers]
                median = statistics.median(preparation)
                mad = statistics.median(abs(value-median) for value in preparation)
                memory = [row['peak_resident_bytes'] for row in raw if row['workers']==workers and row['peak_resident_bytes'] is not None]
                report['statistics'][workers]['preparation'] = {'median_ms': median, 'minimum_ms': min(preparation), 'maximum_ms': max(preparation), 'mad_ms': mad, 'mad_percent': mad/median*100 if median else None}
                report['statistics'][workers]['peak_resident_max_bytes'] = max(memory) if memory else None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print('parallel 3D qualification passed; report: '+str(args.output))


if __name__ == '__main__':
    main()
