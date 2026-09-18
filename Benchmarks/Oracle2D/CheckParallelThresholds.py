#!/usr/bin/env python3
"""Compare complete threshold traces across workers and independent executions."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess


ROW = re.compile(r"parallel kind=(\d+) count=(\d+) workers=(\d+) substeps=(\d+) step=(\d+) dispatch=(\d+) color=(\d+) exact=true")
KINDS = {"contacts": 0, "joints": 1, "bodies": 2, "general-contacts": 3}


def inspect_trace(text, kind, count, workers, substeps, below):
    rows = []
    values = []
    for line in text.splitlines():
        if line.startswith("parallel "):
            match = ROW.fullmatch(line)
            if not match:
                raise ValueError("malformed dispatch record")
            rows.append(tuple(map(int, match.groups())))
        else:
            values.append(line)
    if len(rows) != 4:
        raise ValueError("expected four completed steps")
    for step, row in enumerate(rows):
        if row[:5] != (kind, count, workers, substeps, step):
            raise ValueError("configuration or step mismatch")
    dispatches = sum(row[5] for row in rows)
    if (below and dispatches != 0) or (not below and dispatches == 0):
        raise ValueError("wrong side of parallel dispatch threshold")
    bodies = count if kind == KINDS["bodies"] else 2 * count
    if sum(line.startswith("body ") for line in values) != 4 * bodies:
        raise ValueError("incomplete body trace")
    if sum(line.startswith("events ") for line in values) != 4:
        raise ValueError("incomplete event trace")
    if [line for line in values if line.startswith("step ")] != [f"step {i}" for i in range(4)]:
        raise ValueError("incomplete step trace")
    digest = hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()
    return digest, dispatches, len(values)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--reference", type=Path, help="also compare an earlier build's state traces")
    parser.add_argument("--probe", action="store_true", help="one run per kind before the full grid")
    parser.add_argument("--kind", choices=KINDS, help="qualify one constraint family")
    args = parser.parse_args()
    kinds = [args.kind] if args.kind else KINDS
    binary = args.binary.resolve()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    traces = args.report.with_suffix("")
    traces.mkdir(exist_ok=True)
    signatures = {}
    if args.reference:
        for record in json.loads(args.reference.read_text())["runs"]:
            signatures[tuple(record["state_key"])] = record["sha256"]
    cases = [(kind, level, workers, 4) for kind in kinds
             for level in ["below", "at", "above"] for workers in [2, 4]]
    cases += [(kind, "at", 4, substeps) for kind in kinds for substeps in [1, 2, 8]]
    repetitions = 2
    if args.probe:
        cases = [(kind, "at", 4, 4) for kind in kinds]
        repetitions = 1
    result = {"binary": str(binary), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "runs": []}
    for kind, level, workers, substeps in cases:
        for repeat in range(repetitions):
            command = [str(binary), "--" + kind, "--dump", f"--workers-{workers}", f"--substeps-{substeps}"]
            if level != "at":
                command.append("--" + level)
            name = f"{kind}-{level}-w{workers}-s{substeps}-r{repeat}"
            process = subprocess.run(command, capture_output=True, text=True, timeout=120)
            with gzip.open(traces / (name + ".txt.gz"), "wt") as output:
                output.write(process.stdout)
            (traces / (name + ".stderr.txt")).write_text(process.stderr)
            if process.returncode:
                raise RuntimeError(f"{name}: exit {process.returncode}: {process.stderr}")
            count = (16384 if kind == "bodies" else 4096) + {"below": -1, "at": 0, "above": 1}[level]
            digest, dispatches, lines = inspect_trace(process.stdout, KINDS[kind], count, workers, substeps, level == "below")
            key = (kind, level, substeps)
            if signatures.setdefault(key, digest) != digest:
                raise ValueError(f"{name}: state/event trace differs between workers, repetitions or builds")
            result["runs"].append(dict(name=name, command=command, state_key=key, sha256=digest, lines=lines, dispatches=dispatches))
            args.report.write_text(json.dumps(result, indent=2) + "\n")
            print(f"{name}: exact, dispatches={dispatches}, sha256={digest}", flush=True)


if __name__ == "__main__":
    main()
