#!/usr/bin/env python3
"""Validate the one-point kernel against actual Box2D, then measure separately."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import platform
from pathlib import Path
import statistics
import subprocess
import sys


def execute(binary, *arguments):
    result = subprocess.run([str(binary), *arguments], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"{binary}: exit {result.returncode}: {result.stderr}")
    return result.stdout


def states(output):
    records = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 13 or fields[0] != "STATE":
            raise ValueError(f"invalid state record: {line}")
        key = (int(fields[1]), int(fields[2]))
        values = tuple(map(float, fields[3:]))
        if key in records or not all(map(math.isfinite, values)):
            raise ValueError(f"duplicate/non-finite state: {key}")
        records[key] = values
    if set(records) != {(p, i) for p in range(8) for i in range(16)}:
        raise ValueError("incomplete state coverage")
    return records


def compare_states(reference, candidate):
    if reference.keys() != candidate.keys():
        raise ValueError("different case sets")
    maximum_error = 0.0
    for key in reference:
        for field, (expected, actual) in enumerate(zip(reference[key], candidate[key], strict=True)):
            error = abs(actual - expected)
            maximum_error = max(maximum_error, error)
            # Decimal print rounding plus float32 arithmetic, not a physical
            # settling tolerance. Check every velocity and impulse every pass.
            if not math.isfinite(actual) or error > 2e-6:
                raise ValueError(f"{key} field {field}: {actual} != {expected}")
    return maximum_error


def timing(output):
    fields = output.split()
    if len(fields) != 7 or fields[0] != "KERNEL" or fields[3:5] != ["2048", "2048"]:
        raise ValueError(f"invalid timing record: {output}")
    if (fields[1], fields[2]) not in {("silex", "slots8"), ("clang", "slots8"), ("clang", "packed4")}:
        raise ValueError("unknown engine/layout")
    elapsed, signature = map(float, fields[5:])
    if not math.isfinite(elapsed) or elapsed <= 0 or not math.isfinite(signature):
        raise ValueError("invalid timing/signature")
    return {"engine": fields[1], "layout": fields[2], "elapsed_ms": elapsed, "signature": signature}


def summary(records):
    values = [r["elapsed_ms"] for r in records]
    median = statistics.median(values)
    mad = statistics.median(abs(v - median) for v in values)
    return {"median_ms": median, "min_ms": min(values), "max_ms": max(values), "mad_percent": mad / median * 100}


def parity_result(candidate, reference, admissible):
    if not admissible:
        return "inadmissible"
    if candidate["max_ms"] <= reference["min_ms"]:
        return "demonstrated-for-this-kernel"
    if candidate["min_ms"] > reference["max_ms"]:
        return "missed"
    return "inconclusive"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--silex", required=True, type=Path)
    parser.add_argument("--clang-slots", required=True, type=Path)
    parser.add_argument("--clang-packed", required=True, type=Path)
    parser.add_argument("--box2d-check", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--require-parity", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.check_only and args.require_parity:
        parser.error("--require-parity needs timing")
    binaries = {"silex": args.silex, "clang-slots": args.clang_slots, "clang-packed": args.clang_packed}
    reference = states(execute(args.box2d_check, "--check"))
    result = {"schema": 1, "captured_at": datetime.now(timezone.utc).isoformat(),
              "host": platform.platform(), "machine": platform.machine(),
              "workload": {"contacts": 2048, "passes": 2048, "workers": 1,
                           "float_bits": 32, "fma": True, "allocation_in_kernel": False},
              "oracle_revision": "8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3",
              "correctness": {}, "executables": {}, "warmup": {}, "samples": {}, "summary": {}}
    for name, binary in {**binaries, "box2d-check": args.box2d_check}.items():
        result["executables"][name] = {"path": str(binary), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}
    for name, binary in binaries.items():
        error = compare_states(reference, states(execute(binary, "--check")))
        result["correctness"][name] = {"records": len(reference), "max_absolute_error": error}
        print(f"PASS {name}: 128 records / 1280 scalar comparisons, maximum error {error:g}", flush=True)
    if not args.check_only:
        # Warm-up excluded. Serial processes, rotating order, no compilation.
        for name, binary in binaries.items():
            result["warmup"][name] = timing(execute(binary))
            result["samples"][name] = []
        names = list(binaries)
        signature = result["warmup"]["clang-slots"]["signature"]
        for sample in range(7):
            for name in names[sample % 3:] + names[:sample % 3]:
                record = timing(execute(binaries[name]))
                expected_engine = "silex" if name == "silex" else "clang"
                expected_layout = "packed4" if name == "clang-packed" else "slots8"
                if (record["engine"], record["layout"]) != (expected_engine, expected_layout):
                    raise ValueError(f"wrong executable metadata for {name}")
                if abs(record["signature"] - signature) > 1e-5:
                    raise ValueError(f"different final signature: {name}: {record['signature']} != {signature}")
                result["samples"][name].append(record)
            print(f"sample {sample + 1}/7 complete", flush=True)
        for name in names:
            result["summary"][name] = summary(result["samples"][name])
        result["silex_over_clang_same_layout"] = result["summary"]["silex"]["median_ms"] / result["summary"]["clang-slots"]["median_ms"]
        result["clang_slots_over_packed"] = result["summary"]["clang-slots"]["median_ms"] / result["summary"]["clang-packed"]["median_ms"]
        result["timing_admissible"] = all(s["mad_percent"] <= 5 and s["min_ms"] >= 20 for s in result["summary"].values())
        candidate, reference_time = result["summary"]["silex"], result["summary"]["clang-slots"]
        result["compiler_parity"] = parity_result(candidate, reference_time, result["timing_admissible"])
        print(json.dumps(result["summary"], indent=2))
        print(f"Silex / Clang same layout: {result['silex_over_clang_same_layout']:.4f}")
        print(f"Clang slots / packed: {result['clang_slots_over_packed']:.4f}")
        print(f"Timing admissible: {result['timing_admissible']}")
        print(f"Compiler parity: {result['compiler_parity']}")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    if args.require_parity and result["compiler_parity"] != "demonstrated-for-this-kernel":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
