#!/usr/bin/env python3
"""Compare existing functional joint corpora at equal worker counts."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

CORPORA = {
    "joints": ("joints", ["CheckJoints.py"]),
    "motor_mouse": ("motor_mouse", ["CheckMotorMouse.py"]),
    "joint_tuning": ("joint_tuning", ["CheckJointConstraints.py", "tuning"]),
}


def task_stats(stderr, workers):
    rows = stderr.splitlines()
    if len(rows) != 1 or not rows[0].startswith("ORACLE_TASKS "):
        raise ValueError("missing or unexpected task report")
    stats = dict(part.split("=", 1) for part in rows[0].split()[1:])
    if int(stats["workers"]) != workers:
        raise ValueError("worker configuration differs")
    if int(stats["groups"]) <= 0 or stats["groups"] != stats["finished"]:
        raise ValueError("incomplete task groups")
    if int(stats["items"]) <= 0 or stats["items"] != stats["completed"]:
        raise ValueError("incomplete task items")
    mask = int(stats["mask"])
    if mask <= 0 or mask >= (1 << workers):
        raise ValueError("worker identity outside configured pool")
    # Small functional scenes may use only the caller. Effective parallel work
    # is qualified independently by the pool/world and joint-threshold witnesses.
    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oracle-dir", required=True, type=Path)
    for corpus in CORPORA:
        parser.add_argument("--silex-" + corpus.replace("_", "-"), required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    traces = args.report.with_suffix("")
    traces.mkdir(exist_ok=True)
    signatures = {}
    if args.reference:
        previous = json.loads(args.reference.read_text())["runs"]
        if len(previous) != 18:
            raise ValueError("incomplete reference")
        for row in previous:
            signature = (row["oracle_sha256"], row["silex_sha256"])
            if signatures.setdefault(row["corpus"], signature) != signature:
                raise ValueError("inconsistent reference")
    report = {"runs": [], "binaries": {}}
    for corpus, (target, comparator) in CORPORA.items():
        oracle = (args.oracle_dir / ("gfx_physics_box2d_" + target + "_oracle")).resolve()
        silex = getattr(args, "silex_" + corpus).resolve()
        report["binaries"][corpus] = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in [oracle, silex]}
        default = subprocess.run([str(oracle)], check=True, capture_output=True, text=True, timeout=60)
        task_stats(default.stderr, 1)
        for flags in [("--workers-8",), ("--workers-2", "--workers-4")]:
            invalid = subprocess.run([str(oracle), *flags], capture_output=True, timeout=60)
            if invalid.returncode != 2:
                raise ValueError("oracle accepted invalid worker options")
        for workers in [1, 2, 4]:
            for repeat in range(2):
                name = f"{corpus}-w{workers}-r{repeat}"
                outputs = []
                commands = []
                for engine, binary in [("oracle", oracle), ("silex", silex)]:
                    command = [str(binary), f"--workers-{workers}"]
                    process = subprocess.run(command, capture_output=True, text=True, timeout=120)
                    path = traces / (name + "-" + engine + ".txt")
                    path.write_text(process.stdout)
                    (traces / (name + "-" + engine + ".stderr.txt")).write_text(process.stderr)
                    if process.returncode:
                        raise RuntimeError(f"{name}/{engine}: {process.returncode}: {process.stderr}")
                    if engine == "oracle":
                        stats = task_stats(process.stderr, workers)
                        if process.stdout != default.stdout:
                            raise ValueError("oracle output changed with worker count")
                    elif process.stderr:
                        raise ValueError("unexpected Silex diagnostic")
                    outputs.append(path)
                    commands.append(command)
                signature = tuple(hashlib.sha256(path.read_bytes()).hexdigest() for path in outputs)
                if signatures.setdefault(corpus, signature) != signature:
                    raise ValueError("functional observations differ across workers, repetitions or builds")
                command = [sys.executable, str(Path(__file__).parent / comparator[0]), *comparator[1:], *map(str, outputs)]
                checked = subprocess.run(command, capture_output=True, text=True, timeout=30)
                (traces / (name + "-comparison.txt")).write_text(checked.stdout + checked.stderr)
                if checked.returncode:
                    raise RuntimeError(checked.stdout + checked.stderr)
                report["runs"].append(dict(corpus=corpus, workers=workers, repeat=repeat, commands=commands,
                    oracle_sha256=signature[0], silex_sha256=signature[1], tasks=stats, comparison=checked.stdout.strip()))
                args.report.write_text(json.dumps(report, indent=2) + "\n")
                print(name + ": " + checked.stdout.strip(), flush=True)


if __name__ == "__main__":
    main()
