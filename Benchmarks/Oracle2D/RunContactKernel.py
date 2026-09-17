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
import struct
import subprocess
import sys


def execute(binary, *arguments):
    result = subprocess.run([str(binary), *arguments], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"{binary}: exit {result.returncode}: {result.stderr}")
    return result.stdout


COUNT, PASSES, PATTERNS = 2048, 2048, 16
WEIGHTS = (1, 2, 3, 5, 7, 11, 13, 17, 19, 23)


def float32(value):
    if not math.isfinite(value):
        raise ValueError("non-finite float32 state")
    try:
        return struct.unpack("<f", struct.pack("<f", value))[0]
    except OverflowError as error:
        raise ValueError("state outside float32 range") from error


def states(output, full=False):
    records = {}
    for line in output.splitlines():
        fields = line.split()
        if len(fields) != 13 or fields[0] != "STATE":
            raise ValueError(f"invalid state record: {line}")
        key = (int(fields[1]), int(fields[2]))
        # Both emitters print float32 states, using different decimal formats.
        # Nine significant C digits and Silex's format round-trip to float32.
        values = tuple(float32(float(value)) for value in fields[3:])
        if key in records or not all(map(math.isfinite, values)):
            raise ValueError(f"duplicate/non-finite state: {key}")
        records[key] = values
    if set(records) != {(p, i) for p in range(PASSES if full else 8) for i in range(PATTERNS)}:
        raise ValueError("incomplete state coverage")
    return records


def check_totals(records):
    for (step, index), values in records.items():
        previous = 0.0 if step == 0 else records[step - 1, index][8]
        if values[8] != float32(previous + values[6]):
            raise ValueError(f"incorrect total impulse recurrence: {(step, index)}")


def replay(binary, candidate):
    rows = ["STATE " + " ".join(map(str, (*key, *values)))
            for key, values in sorted(candidate.items())]
    result = subprocess.run([str(binary), "--check-replay"], input="\n".join(rows) + "\n",
                            capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(f"oracle replay exit {result.returncode}: {result.stderr}")
    return states(result.stdout, full=True)


def signature_interval(records):
    total = magnitude = 0.0
    for index in range(PATTERNS):
        terms = [value * weight for value, weight in zip(records[PASSES - 1, index], WEIGHTS, strict=True)]
        total += sum(terms)
        magnitude += sum(map(abs, terms))
    # At most two float32 operations per weighted term. This conservative
    # bound also covers decimal signature printing, as in RunStageKernels.
    repeats = COUNT // PATTERNS
    allowance = (2 * len(WEIGHTS) * 2**-23 * magnitude + 1e-5) * repeats
    return total * repeats, allowance


def compare_states(reference, candidate):
    if reference.keys() != candidate.keys():
        raise ValueError("different case sets")
    maximum_error = 0.0
    for key in reference:
        for field, (expected, actual) in enumerate(zip(reference[key], candidate[key], strict=True)):
            error = abs(actual - expected)
            maximum_error = max(maximum_error, error)
            # The original local arithmetic allowance is unchanged. Long
            # runs use identical-input replay, not a looser settling tolerance.
            if not math.isfinite(actual) or error > 2e-6:
                raise ValueError(f"{key} field {field}: {actual} != {expected}")
    return maximum_error


def add_layout_arguments(parser):
    parser.add_argument("--silex-layout", required=True, choices=("slots8", "packed4"),
                        help="Verified binary layout: current native=slots8, LLVM=packed4; record build provenance")
    parser.add_argument("--baseline-silex-layout", choices=("slots8", "packed4"))


def layout_configuration(parser, args):
    if bool(args.baseline_silex) != bool(args.baseline_silex_layout):
        parser.error("--baseline-silex and --baseline-silex-layout must be supplied together")
    layouts = {"silex": args.silex_layout, "clang-slots": "slots8", "clang-packed": "packed4"}
    if args.baseline_silex:
        layouts["silex-before"] = args.baseline_silex_layout
    return layouts


def matching_clang(layout):
    return {"slots8": "clang-slots", "packed4": "clang-packed"}[layout]


def timing(output):
    fields = output.split()
    if len(fields) != 7 or fields[0] != "KERNEL" or fields[3:5] != ["2048", "2048"]:
        raise ValueError(f"invalid timing record: {output}")
    if (fields[1], fields[2]) not in {("silex", "private"), ("clang", "slots8"), ("clang", "packed4")}:
        raise ValueError("unknown engine/layout")
    elapsed, signature = map(float, fields[5:])
    if not math.isfinite(elapsed) or elapsed <= 0 or not math.isfinite(signature):
        raise ValueError("invalid timing/signature")
    return {"engine": fields[1], "layout": fields[2], "elapsed_ms": elapsed, "signature": signature}


def checked_timing(output, name, signature, layout):
    record = timing(output)
    expected_engine = "silex" if name.startswith("silex") else "clang"
    expected_layout = "private" if name.startswith("silex") else layout
    if (record["engine"], record["layout"]) != (expected_engine, expected_layout):
        raise ValueError(f"wrong executable metadata for {name}")
    expected, allowance = signature
    if abs(record["signature"] - expected) > allowance:
        raise ValueError(f"timed signature differs from verified final states: {name}")
    record["layout"] = layout
    return record


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
    parser.add_argument("--baseline-silex", type=Path, help="Include the compiler baseline in the same alternating series")
    parser.add_argument("--clang-slots", required=True, type=Path)
    parser.add_argument("--clang-packed", required=True, type=Path)
    parser.add_argument("--box2d-check", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument("--require-parity", action="store_true")
    parser.add_argument("--output", type=Path)
    add_layout_arguments(parser)
    args = parser.parse_args()
    layouts = layout_configuration(parser, args)
    if args.check_only and args.require_parity:
        parser.error("--require-parity needs timing")
    binaries = {"silex": args.silex, "clang-slots": args.clang_slots, "clang-packed": args.clang_packed}
    if args.baseline_silex:
        binaries["silex-before"] = args.baseline_silex
    reference = states(execute(args.box2d_check, "--check"))
    full_reference = states(execute(args.box2d_check, "--check-full"), full=True)
    check_totals(reference)
    check_totals(full_reference)
    result = {"schema": 3, "captured_at": datetime.now(timezone.utc).isoformat(),
              "host": platform.platform(), "machine": platform.machine(),
              "workload": {"contacts": 2048, "passes": 2048, "workers": 1,
                           "float_bits": 32, "layouts": layouts, "allocation_in_kernel": False},
              "oracle_revision": "8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3",
              "numerical_budgets": {"local_absolute": 2e-6, "state_type": "float32",
                                    "total_recurrence": "exact float32", "full": "identical-input replay"},
              "correctness": {}, "executables": {}, "warmup": {}, "samples": {}, "summary": {}}
    for name, binary in {**binaries, "box2d-check": args.box2d_check}.items():
        result["executables"][name] = {"path": str(binary), "sha256": hashlib.sha256(binary.read_bytes()).hexdigest()}
    signatures = {}
    for name, binary in binaries.items():
        short = states(execute(binary, "--check"))
        check_totals(short)
        short_error = compare_states(reference, short)
        full = states(execute(binary, "--check-full"), full=True)
        check_totals(full)
        full_error = compare_states(replay(args.box2d_check, full), full)
        independent_error = max(abs(a - b) for key in full
                                for a, b in zip(full[key], full_reference[key], strict=True))
        signatures[name] = signature_interval(full)
        result["correctness"][name] = {
            "short": {"records": len(short), "max_absolute_error": short_error},
            "full": {"records": len(full), "max_local_error": full_error,
                     "independent_trajectory_max_error": independent_error,
                     "oracle": "every transition from identical candidate inputs",
                     "total_recurrence": "exact float32"},
            "signature_center": signatures[name][0], "signature_allowance": signatures[name][1]}
        print(f"PASS {name}: 128 short states and 32768 replayed transitions; local error {full_error:g}", flush=True)
    if not args.check_only:
        # Warm-up excluded. Serial processes, rotating order, no compilation.
        for name, binary in binaries.items():
            result["warmup"][name] = checked_timing(execute(binary), name, signatures[name], layouts[name])
            result["samples"][name] = []
        names = list(binaries)
        for sample in range(7):
            offset = sample % len(names)
            for name in names[offset:] + names[:offset]:
                record = checked_timing(execute(binaries[name]), name, signatures[name], layouts[name])
                if record["signature"] != result["warmup"][name]["signature"]:
                    raise ValueError(f"unstable final signature: {name}")
                result["samples"][name].append(record)
            print(f"sample {sample + 1}/7 complete", flush=True)
        for name in names:
            result["summary"][name] = summary(result["samples"][name])
        result["same_layout_reference"] = matching_clang(args.silex_layout)
        result["silex_over_clang_same_layout"] = result["summary"]["silex"]["median_ms"] / result["summary"][result["same_layout_reference"]]["median_ms"]
        result["clang_slots_over_packed"] = result["summary"]["clang-slots"]["median_ms"] / result["summary"]["clang-packed"]["median_ms"]
        result["timing_admissible"] = all(s["mad_percent"] <= 5 and s["min_ms"] >= 20 for s in result["summary"].values())
        candidate, reference_time = result["summary"]["silex"], result["summary"][result["same_layout_reference"]]
        result["compiler_parity"] = parity_result(candidate, reference_time, result["timing_admissible"])
        if args.baseline_silex:
            before = result["summary"]["silex-before"]
            result["silex_after_over_before"] = candidate["median_ms"] / before["median_ms"]
            result["silex_after_over_before_observed_range"] = [
                candidate["min_ms"] / before["max_ms"], candidate["max_ms"] / before["min_ms"]]
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
