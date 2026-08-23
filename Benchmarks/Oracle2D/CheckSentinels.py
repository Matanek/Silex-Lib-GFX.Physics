#!/usr/bin/env python3

"""Validate statistical records emitted by the four GFX sentinels."""

from __future__ import annotations

import argparse
import math
import pathlib
import statistics
import sys
from collections import defaultdict


def fields(line: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for field in line.split()[1:]:
        if "=" in field:
            key, value = field.split("=", 1)
            result[key] = value
    return result


def load(paths: list[pathlib.Path]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    sources = [("<stdin>", sys.stdin)] if not paths else [
        (str(path), path.open(encoding="utf-8")) for path in paths
    ]
    try:
        for source, stream in sources:
            for line_number, raw_line in enumerate(stream, 1):
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                values = fields(line)
                if line.startswith("SILEX_GFX_BOIDS "):
                    count = values.get("count")
                    if count == "4000":
                        grouped["boids-kernel-4000"].append(values)
                    elif count == "2000":
                        grouped["boids-example-2000"].append(values)
                    else:
                        raise ValueError(f"{source}:{line_number}: unexpected Boids count {count!r}")
                elif line.startswith("SILEX_GFX_WORLD "):
                    grouped["world-example"].append(values)
                else:
                    raise ValueError(f"{source}:{line_number}: unknown sentinel record")
    finally:
        for _, stream in sources:
            if stream is not sys.stdin:
                stream.close()
    if not grouped:
        raise ValueError("no sentinel record found")
    return grouped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", type=pathlib.Path)
    parser.add_argument(
        "--boids-kernel-baseline",
        type=float,
        help="accepted median FPS; the new 4,000-boid median must retain at least 95%%",
    )
    parser.add_argument("--enforce", action="store_true")
    arguments = parser.parse_args()
    try:
        grouped = load(arguments.paths)
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    all_failures: list[str] = []
    for name in sorted(grouped):
        records = grouped[name]
        failures: list[str] = []
        if len(records) != 7:
            failures.append(f"expected 7 measured runs, got {len(records)}")
        fps_values: list[float] = []
        for record in records:
            if record.get("present") != "immediate":
                failures.append("presentation is not recorded as immediate")
            if name == "world-example" and record.get("focus") != "focused":
                failures.append("World window is not recorded as focused")
            try:
                fps = float(record["fps"])
            except (KeyError, ValueError):
                failures.append("missing or invalid fps")
                continue
            if not math.isfinite(fps) or fps <= 0.0:
                failures.append("fps is not finite and positive")
            fps_values.append(fps)

        if fps_values:
            median = statistics.median(fps_values)
            mad = statistics.median(abs(value - median) for value in fps_values)
            relative_mad = mad / median
            if relative_mad > 0.05:
                failures.append(f"MAD {relative_mad * 100.0:.2f}% exceeds 5%")
            if name in {"boids-example-2000", "world-example"} and median < 120.0:
                failures.append(f"median {median:.3f} FPS is below 120 FPS")
            if name == "boids-kernel-4000" and arguments.boids_kernel_baseline is not None:
                minimum = arguments.boids_kernel_baseline * 0.95
                if median < minimum:
                    failures.append(
                        f"median {median:.3f} FPS is below 95% of baseline ({minimum:.3f} FPS)"
                    )
            summary = (
                f"n={len(fps_values)} median={median:.3f}fps min={min(fps_values):.3f}fps "
                f"max={max(fps_values):.3f}fps mad={mad:.3f}fps ({relative_mad * 100.0:.2f}%)"
            )
        else:
            summary = "no valid FPS value"
        status = "PASS" if not failures else "FAIL"
        print(f"{status} {name}: {summary}")
        for failure in sorted(set(failures)):
            print(f"  - {failure}")
            all_failures.append(f"{name}: {failure}")
    return 1 if arguments.enforce and all_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
