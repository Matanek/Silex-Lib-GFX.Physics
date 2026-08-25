#!/usr/bin/env python3

"""Validate and summarize SILEX_PHYSICS_CORPUS records."""

from __future__ import annotations

import argparse
import math
import pathlib
import re
import statistics
import sys
from collections import defaultdict


FLOAT_FIELDS = (
    "dt",
    "elapsed_ms",
    "step_ms",
    "centroid_x",
    "centroid_y",
    "max_speed",
    "min_y",
    "max_overlap_mm",
    "state_signature",
)

CADENCE_GATES_MS = {
    "sparse-1000": 4.00,
    "sparse-5000": 16.67,
    "sparse-10000": 33.33,
    "pile-1000": 33.33,
    "circle-1800": 16.67,
}

CADENCE_TARGETS_MS = {
    "circle-5000": 16.67,
}

BODY_RSS_BUDGET_BYTES = 1024
PERSISTENT_PAIR_RSS_BUDGET_BYTES = 512


def parse_record(line: str, source: str, line_number: int) -> dict[str, str]:
    prefix = "SILEX_PHYSICS_CORPUS "
    if not line.startswith(prefix):
        raise ValueError(f"{source}:{line_number}: expected {prefix.strip()}")
    record: dict[str, str] = {}
    for field in line[len(prefix) :].split():
        if "=" not in field:
            raise ValueError(f"{source}:{line_number}: malformed field {field!r}")
        key, value = field.split("=", 1)
        if key in record:
            raise ValueError(f"{source}:{line_number}: duplicate field {key!r}")
        record[key] = value
    required = {
        "engine",
        "scenario",
        "mode",
        "workers",
        "bodies",
        "steps",
        "contacts",
        *FLOAT_FIELDS,
    }
    missing = sorted(required - record.keys())
    if missing:
        raise ValueError(f"{source}:{line_number}: missing fields: {', '.join(missing)}")
    for key in FLOAT_FIELDS:
        value = float(record[key])
        if not math.isfinite(value):
            raise ValueError(f"{source}:{line_number}: {key} is not finite")
    return record


def load_records(paths: list[pathlib.Path]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    rss_pattern = re.compile(r"^# run=\d+ rss_bytes=(\d+)(?:\s|$)")
    if not paths:
        sources = [("<stdin>", sys.stdin)]
    else:
        sources = [(str(path), path.open(encoding="utf-8")) for path in paths]
    try:
        for source, stream in sources:
            pending_rss: str | None = None
            for line_number, raw_line in enumerate(stream, 1):
                line = raw_line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    match = rss_pattern.match(line)
                    if match:
                        pending_rss = match.group(1)
                    continue
                record = parse_record(line, source, line_number)
                if pending_rss is not None:
                    record["_rss_bytes"] = pending_rss
                    pending_rss = None
                records.append(record)
    finally:
        for _, stream in sources:
            if stream is not sys.stdin:
                stream.close()
    if not records:
        raise ValueError("no corpus record found")
    return records


def sparse_expected_centroid(body_count: int) -> tuple[float, float]:
    x_total = 0.0
    y_total = 0.0
    for index in range(body_count):
        x_total += (index % 100) * 1.25 + 4.0
        y_total += (index // 100) * 1.25 + 0.5
    return x_total / body_count, y_total / body_count


def correction_failures(record: dict[str, str]) -> list[str]:
    scenario = record["scenario"]
    centroid_x = float(record["centroid_x"])
    centroid_y = float(record["centroid_y"])
    maximum_speed = float(record["max_speed"])
    minimum_y = float(record["min_y"])
    maximum_overlap = float(record["max_overlap_mm"])
    contacts = int(record["contacts"])
    failures: list[str] = []

    if scenario == "release-parity":
        if not 0.495 <= centroid_y <= 0.505:
            failures.append(f"center y {centroid_y:.6f} is outside [0.495, 0.505]")
        if maximum_speed > 0.005:
            failures.append(f"speed {maximum_speed:.6f} exceeds 0.005 m/s")
    elif scenario.startswith("sparse-"):
        body_count = int(record["bodies"])
        expected_x, expected_y = sparse_expected_centroid(body_count)
        if contacts != 0:
            failures.append(f"expected zero contacts, got {contacts}")
        if abs(centroid_x - expected_x) > 0.001 or abs(centroid_y - expected_y) > 0.001:
            failures.append(
                f"centroid ({centroid_x:.6f}, {centroid_y:.6f}) differs from "
                f"({expected_x:.6f}, {expected_y:.6f})"
            )
    elif scenario == "pile-1000":
        if minimum_y < 0.195:
            failures.append(f"minimum y {minimum_y:.6f} is below 0.195 m")
    elif scenario == "circle-1800":
        if minimum_y < -2.952:
            failures.append(f"minimum y {minimum_y:.6f} is below -2.952 m")
        if maximum_overlap > 12.0:
            failures.append(f"overlap {maximum_overlap:.6f} exceeds 12 mm")
    elif scenario == "circle-5000":
        if minimum_y < -2.978:
            failures.append(f"minimum y {minimum_y:.6f} is below -2.978 m")
        if maximum_overlap > 20.0:
            failures.append(f"overlap {maximum_overlap:.6f} exceeds 20 mm")
    else:
        failures.append(f"unknown scenario {scenario!r}")
    return failures


def summarize(records: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    reports: list[str] = []
    failures: list[str] = []
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for record in records:
        key = (record["engine"], record["scenario"], record["mode"], record["workers"])
        grouped[key].append(record)

    signatures_by_configuration: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    workers_by_configuration: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for record in records:
        key = (record["engine"], record["scenario"], record["mode"])
        signatures_by_configuration[key].add(record["state_signature"])
        workers_by_configuration[key].add(record["workers"])

    for key in sorted(signatures_by_configuration):
        worker_counts = workers_by_configuration[key]
        signatures = signatures_by_configuration[key]
        if len(worker_counts) > 1 and len(signatures) != 1:
            engine, scenario, mode = key
            reports.append(
                f"FAIL {engine}/{scenario}/{mode}/worker-matrix: "
                "state_signature changed across worker counts"
            )
            failures.append(
                f"{engine}/{scenario}/{mode}: state_signature changed across worker counts"
            )

    rss_baselines: dict[tuple[str, str, str], float] = {}
    for (engine, scenario, mode, workers), group in grouped.items():
        rss_values = [int(record["_rss_bytes"]) for record in group if "_rss_bytes" in record]
        if scenario == "release-parity" and len(rss_values) >= 7:
            rss_baselines[(engine, mode, workers)] = statistics.median(rss_values)

    for key in sorted(grouped):
        engine, scenario, mode, workers = key
        group = grouped[key]
        label = f"{engine}/{scenario}/{mode}/workers-{workers}"
        group_failures: list[str] = []
        group_notes: list[str] = []
        for record in group:
            group_failures.extend(correction_failures(record))

        signatures = {record["state_signature"] for record in group}
        if len(signatures) != 1:
            group_failures.append("state_signature changed across identical runs")

        times = [float(record["step_ms"]) for record in group]
        median = statistics.median(times)
        absolute_deviations = [abs(value - median) for value in times]
        mad = statistics.median(absolute_deviations)
        relative_mad = mad / median if median > 0.0 else math.inf
        timing = (
            f"n={len(group)} median={median:.6f}ms min={min(times):.6f}ms "
            f"max={max(times):.6f}ms mad={mad:.6f}ms ({relative_mad * 100.0:.2f}%)"
        )
        rss_records = [record for record in group if "_rss_bytes" in record]
        rss_values = [int(record["_rss_bytes"]) for record in rss_records]
        if rss_values:
            timing += f" rss_median={statistics.median(rss_values):.0f}B"

        if len(group) >= 7 and relative_mad > 0.05:
            group_failures.append(f"timing MAD {relative_mad * 100.0:.2f}% exceeds 5%")
        if engine.startswith("silex") and mode == "release" and len(group) >= 7:
            budget = CADENCE_GATES_MS.get(scenario)
            if budget is not None and median > budget:
                group_failures.append(f"median {median:.6f} ms exceeds {budget:.2f} ms budget")
            target = CADENCE_TARGETS_MS.get(scenario)
            if target is not None and median > target:
                group_notes.append(
                    f"cadence target missed: median {median:.6f} ms exceeds {target:.2f} ms"
                )
            if scenario in {"sparse-10000", "circle-5000"} and len(rss_values) >= 7:
                baseline = rss_baselines.get((engine, mode, workers))
                if baseline is not None:
                    rss_median = statistics.median(rss_values)
                    body_count = int(group[0]["bodies"])
                    incremental_rss = rss_median - baseline
                    allowed_rss = BODY_RSS_BUDGET_BYTES * body_count
                    if scenario == "circle-5000":
                        if any("persistent_pairs" not in record for record in rss_records):
                            group_failures.append(
                                "dense memory records require persistent_pairs"
                            )
                        else:
                            pair_counts = {
                                int(record["persistent_pairs"]) for record in rss_records
                            }
                            if len(pair_counts) != 1:
                                group_failures.append(
                                    "persistent_pairs changed across identical runs"
                                )
                            allowed_rss += (
                                PERSISTENT_PAIR_RSS_BUDGET_BYTES *
                                max(pair_counts)
                            )
                    bytes_per_body = incremental_rss / body_count
                    if incremental_rss > allowed_rss:
                        group_failures.append(
                            f"incremental RSS {incremental_rss:.0f} B "
                            f"({bytes_per_body:.3f} B/body) exceeds "
                            f"{allowed_rss} B storage budget"
                        )

        status = "PASS" if not group_failures else "FAIL"
        note = "" if not group_notes else f"; {'; '.join(group_notes)}"
        reports.append(f"{status} {label}: {timing}{note}")
        failures.extend(f"{label}: {failure}" for failure in sorted(set(group_failures)))
    return reports, failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=pathlib.Path)
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="return a non-zero status when a correction, determinism, variance or cadence gate fails",
    )
    arguments = parser.parse_args()
    try:
        records = load_records(arguments.paths)
        reports, failures = summarize(records)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    for report in reports:
        print(report)
    for failure in failures:
        print(f"  - {failure}")
    return 1 if arguments.enforce and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
