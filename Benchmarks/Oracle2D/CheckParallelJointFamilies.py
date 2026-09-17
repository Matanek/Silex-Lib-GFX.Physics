#!/usr/bin/env python3
"""Check exact joint-family state traces under effective constraint dispatch."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROW = re.compile(r"families workers=(\d+) substeps=(\d+) step=(\d+) dispatch=(\d+) color=(\d+) exact=true")


def inspect_trace(text, workers, substeps):
    rows, values = [], []
    for line in text.splitlines():
        if line.startswith("families "):
            match = ROW.fullmatch(line)
            if not match:
                raise ValueError("malformed dispatch record")
            rows.append(tuple(map(int, match.groups())))
        else:
            values.append(line)
    if len(rows) != 8:
        raise ValueError("expected eight completed steps")
    for step, row in enumerate(rows):
        if row[:3] != (workers, substeps, step):
            raise ValueError("configuration or step mismatch")
        if row[3] <= 0 or row[4] != 4096:
            raise ValueError("missing effective constraint dispatch")
    if [line for line in values if line.startswith("step ")] != [f"step {i}" for i in range(8)]:
        raise ValueError("incomplete step trace")
    if sum(line.startswith("body ") for line in values) != 8 * 8192:
        raise ValueError("incomplete body trace")
    joints = [line.split() for line in values if line.startswith("joint ")]
    if len(joints) != 8 * 4096:
        raise ValueError("incomplete joint trace")
    for index, joint in enumerate(joints):
        identity = index % 4096
        if len(joint) != 8 or (int(joint[1]), int(joint[2])) != (identity % 7, identity):
            raise ValueError("joint family or identity order differs")
    digest = hashlib.sha256(("\n".join(values) + "\n").encode()).hexdigest()
    return digest, sum(row[3] for row in rows), len(values)


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
    signatures = {}
    if args.reference:
        previous = json.loads(args.reference.read_text())["runs"]
        if len(previous) != 16:
            raise ValueError("incomplete reference")
        for row in previous:
            if signatures.setdefault(row["substeps"], row["sha256"]) != row["sha256"]:
                raise ValueError("inconsistent reference")
    result = {"binary": str(binary), "binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(), "runs": []}
    for substeps in [1, 2, 4, 8]:
        for workers in [2, 4]:
            for repeat in range(2):
                name = f"joints-s{substeps}-w{workers}-r{repeat}"
                command = [str(binary), f"--workers-{workers}", f"--substeps-{substeps}", "--dump"]
                process = subprocess.run(command, capture_output=True, text=True, timeout=120)
                with gzip.open(traces / (name + ".txt.gz"), "wt") as output:
                    output.write(process.stdout)
                (traces / (name + ".stderr.txt")).write_text(process.stderr)
                if process.returncode:
                    raise RuntimeError(f"{name}: exit {process.returncode}: {process.stderr}")
                digest, dispatches, lines = inspect_trace(process.stdout, workers, substeps)
                if signatures.setdefault(substeps, digest) != digest:
                    raise ValueError(f"{name}: state trace differs between workers, repetitions or builds")
                result["runs"].append(dict(name=name, command=command, substeps=substeps, sha256=digest, dispatches=dispatches, lines=lines))
                args.report.write_text(json.dumps(result, indent=2) + "\n")
                print(f"{name}: exact, dispatches={dispatches}, sha256={digest}", flush=True)


if __name__ == "__main__":
    main()
