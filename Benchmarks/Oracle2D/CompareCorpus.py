#!/usr/bin/env python3
"""Compare matched Box2D/Silex workloads, never an absolute FPS budget."""

from __future__ import annotations

import argparse
import math
import pathlib
import statistics
from collections import defaultdict

from CheckCorpus import correction_failures, load_records


WORKLOAD = "box2d-3.1.1-v1"
NUMERIC_CONFIGURATION = (
    "bodies", "steps", "dt", "substeps", "workers", "gravity_y",
    "contact_hertz", "contact_damping", "body_mass",
)


def compare(records: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    groups: dict[str, dict[str, list[dict[str, str]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    failures: list[str] = []
    reports: list[str] = []
    for record in records:
        engine = record["engine"]
        if engine not in {"box2d-3.1.1", "silex-current"}:
            failures.append(f"unsupported engine {engine}")
            continue
        if record.get("workload") != WORKLOAD or record.get("schema") != "2":
            failures.append(f"{engine}: matched workload metadata required")
            continue
        if record["mode"] != "release":
            failures.append(f"{engine}: Release measurements required")
            continue
        missing = [key for key in (*NUMERIC_CONFIGURATION, "sleep_enabled")
                   if key not in record]
        if missing:
            failures.append(f"{engine}: missing configuration {missing}")
            continue
        if any(not math.isfinite(float(record[key])) for key in NUMERIC_CONFIGURATION):
            failures.append(f"{engine}: non-finite configuration")
            continue
        if float(record["step_ms"]) <= 0:
            failures.append(f"{engine}: positive step time required")
            continue
        failures.extend(f"{engine}/{record['scenario']}: {failure}"
                        for failure in correction_failures(record))
        if record["scenario"].startswith(("circle-", "sparse-")):
            if int(record.get("awake", "-1")) != int(record["bodies"]):
                failures.append(f"{engine}: all bodies must remain awake")
        groups[record["scenario"]][engine].append(record)

    for scenario, engines in sorted(groups.items()):
        if set(engines) != {"box2d-3.1.1", "silex-current"}:
            failures.append(f"{scenario}: both engines required")
            continue
        oracle = engines["box2d-3.1.1"]
        silex = engines["silex-current"]
        combined = oracle + silex
        configuration_ok = True
        for key in NUMERIC_CONFIGURATION:
            values = [float(record[key]) for record in combined]
            if any(not math.isclose(value, values[0], rel_tol=1e-7, abs_tol=0)
                   for value in values[1:]):
                failures.append(f"{scenario}: mismatched {key}")
                configuration_ok = False
        if len({record["sleep_enabled"] for record in combined}) != 1:
            failures.append(f"{scenario}: mismatched sleep_enabled")
            configuration_ok = False
        if not configuration_ok:
            continue
        if len(oracle) < 7 or len(silex) < 7 or len(oracle) != len(silex):
            failures.append(f"{scenario}: equal series of at least seven runs required")
            continue
        medians: dict[str, float] = {}
        for engine, group in engines.items():
            if len({record["state_signature"] for record in group}) != 1:
                failures.append(f"{scenario}/{engine}: nondeterministic state")
            times = [float(record["step_ms"]) for record in group]
            median = statistics.median(times)
            mad = statistics.median(abs(value - median) for value in times)
            if mad / median > 0.05:
                failures.append(f"{scenario}/{engine}: MAD exceeds 5%")
            medians[engine] = median
            reports.append(
                f"{scenario}/{engine}: n={len(times)} median={median:.6f}ms "
                f"min={min(times):.6f}ms max={max(times):.6f}ms "
                f"MAD={100 * mad / median:.3f}%"
            )
        ratio = medians["silex-current"] / medians["box2d-3.1.1"]
        reports.append(f"{scenario}: Silex/Box2D={ratio:.6f} target<=1")
        if ratio > 1:
            failures.append(f"{scenario}: Silex/Box2D={ratio:.6f} exceeds parity")
        elif max(float(row["step_ms"]) for row in silex) > min(
            float(row["step_ms"]) for row in oracle
        ):
            # Conservative gate: overlapping observed ranges need a more precise
            # campaign; measurement noise is not a fixed allowed slowdown.
            failures.append(f"{scenario}: overlapping timing ranges; parity inconclusive")
    if not groups:
        failures.append("no matched workload")
    return reports, sorted(set(failures))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=pathlib.Path)
    arguments = parser.parse_args()
    try:
        reports, failures = compare(load_records(arguments.paths))
    except (OSError, ValueError, KeyError) as error:
        print(f"ERROR {error}")
        return 2
    for report in reports:
        print(report)
    for failure in failures:
        print(f"FAIL {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
