#!/usr/bin/env python3
"""Compare full lifecycle traces across workers, repetitions and build modes."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROW = re.compile(r"lifecycle workers=(\d+) step=(\d+) dispatch=(\d+) color=(\d+) exact=true")
COMPLETED = "completed sleep=true hit=true sensor_begin=true sensor_end=true callback=true ccd=true"


def inspect_trace(text, workers):
    rows, values = [], []
    for line in text.splitlines():
        if line.startswith("lifecycle "):
            match = ROW.fullmatch(line)
            if not match:
                raise ValueError("malformed dispatch record")
            rows.append(tuple(map(int, match.groups())))
        else:
            values.append(line)
    if len(rows) != 44:
        raise ValueError("expected 44 completed steps")
    for step, (actual_workers, actual_step, dispatch, _) in enumerate(rows):
        if (actual_workers, actual_step) != (workers, step):
            raise ValueError("configuration or step mismatch")
        if (step == 10 and dispatch != 0) or (step != 10 and dispatch <= 0):
            raise ValueError("expected effective dispatch except at zero time step")
    if [line for line in values if line.startswith("step ")] != [f"step {i}" for i in range(44)]:
        raise ValueError("incomplete step trace")
    if values[-1:] != [COMPLETED]:
        raise ValueError("missing lifecycle coverage assertion")
    for prefix in ["events ", "ccd "]:
        if sum(line.startswith(prefix) for line in values) != 44:
            raise ValueError("incomplete event or CCD trace")
    for prefix in ["callback ", "sensor_begin ", "sensor_end ", "hit ", "invalid "]:
        if not any(line.startswith(prefix) for line in values):
            raise ValueError("missing lifecycle channel: " + prefix)
    # Seven special bodies initially; recreation adds one retained handle at step 5.
    expected_bodies = 5 * (16384 + 7) + 39 * (16384 + 8)
    if sum(line.startswith(("body ", "invalid ")) for line in values) != expected_bodies:
        raise ValueError("incomplete body trace")
    digest = hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()
    return digest, sum(row[2] for row in rows), len(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--reference", type=Path)
    args = parser.parse_args()
    binary = args.binary.resolve()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    traces = args.report.with_suffix("")
    traces.mkdir(exist_ok=True)
    expected = None
    if args.reference:
        previous = json.loads(args.reference.read_text())["runs"]
        if len(previous) != 4 or len({row["sha256"] for row in previous}) != 1:
            raise ValueError("incomplete or inconsistent reference")
        expected = previous[0]["sha256"]
    result = {"binary": str(binary), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "runs": []}
    for workers in [2, 4]:
        for repeat in range(2):
            name = f"lifecycle-w{workers}-r{repeat}"
            command = [str(binary), f"--workers-{workers}", "--dump"]
            process = subprocess.run(command, capture_output=True, text=True, timeout=180)
            with gzip.open(traces / (name + ".txt.gz"), "wt") as output:
                output.write(process.stdout)
            (traces / (name + ".stderr.txt")).write_text(process.stderr)
            if process.returncode:
                raise RuntimeError(f"{name}: exit {process.returncode}: {process.stderr}")
            digest, dispatches, lines = inspect_trace(process.stdout, workers)
            if expected is None:
                expected = digest
            if expected != digest:
                raise ValueError(f"{name}: state/event trace differs between workers, repetitions or builds")
            result["runs"].append(dict(name=name, command=command, sha256=digest, dispatches=dispatches, lines=lines))
            args.report.write_text(json.dumps(result, indent=2) + "\n")
            print(f"{name}: exact, dispatches={dispatches}, sha256={digest}", flush=True)


if __name__ == "__main__":
    main()
