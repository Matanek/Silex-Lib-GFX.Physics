#!/usr/bin/env python3

"""Validate the executable GFX.Physics / Box2D completeness contract."""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
from collections import Counter


STATUSES = {"covered", "partial", "planned", "divergent", "excluded"}
REQUIRED_HEADERS = (
    "base.h",
    "math_functions.h",
    "types.h",
    "collision.h",
    "box2d.h",
)
API_PATTERN = re.compile(
    r"B2_API\s+[^;{]*?\b(b2[A-Za-z0-9_]+)\s*\(",
    re.DOTALL,
)


def fail(message: str) -> None:
    raise ValueError(message)


def load_matrix(path: pathlib.Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot load matrix {path}: {error}")
    if not isinstance(value, dict):
        fail("matrix root must be an object")
    return value


def box2d_revision(source: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(source), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def box2d_version(source: pathlib.Path) -> str:
    cmake = (source / "CMakeLists.txt").read_text(encoding="utf-8")
    match = re.search(
        r"project\s*\(\s*box2d\s+VERSION\s+([0-9]+(?:\.[0-9]+)+)",
        cmake,
        re.IGNORECASE,
    )
    if match is None:
        fail("cannot read the Box2D project version")
    return match.group(1)


def public_symbols(source: pathlib.Path) -> tuple[dict[str, list[str]], list[str]]:
    include = source / "include" / "box2d"
    by_header: dict[str, list[str]] = {}
    all_symbols: list[str] = []
    for name in REQUIRED_HEADERS:
        path = include / name
        if not path.is_file():
            fail(f"missing pinned public header: {path}")
        symbols = API_PATTERN.findall(path.read_text(encoding="utf-8"))
        if not symbols:
            fail(f"no B2_API symbol found in {path}")
        by_header[name] = symbols
        all_symbols.extend(symbols)
    duplicates = sorted(symbol for symbol, count in Counter(all_symbols).items() if count != 1)
    if duplicates:
        fail(f"public symbols are not unique: {', '.join(duplicates)}")
    return by_header, sorted(all_symbols)


def validate_evidence(
    package_root: pathlib.Path,
    tracking_specs: set[str],
    row: dict,
) -> None:
    row_id = row["id"]
    evidence = row.get("evidence", [])
    tracking = row.get("tracking")
    rationale = row.get("rationale")
    status = row["status"]
    if not isinstance(evidence, list) or any(not isinstance(item, str) or not item for item in evidence):
        fail(f"{row_id}: evidence must be a list of non-empty paths")
    if status in {"covered", "partial", "divergent"} and not evidence:
        fail(f"{row_id}: {status} capability requires executable or consumer evidence")
    if status in {"partial", "planned"} and not isinstance(tracking, str):
        fail(f"{row_id}: {status} capability requires a future Spec")
    if tracking is not None and tracking not in tracking_specs:
        fail(f"{row_id}: unknown future Spec: {tracking!r}")
    if status in {"divergent", "excluded"} and (
        not isinstance(rationale, str) or not rationale
    ):
        fail(f"{row_id}: {status} capability requires an explicit rationale")
    for item in evidence:
        path = package_root / item.split("#", 1)[0]
        if not path.exists():
            fail(f"{row_id}: evidence does not exist: {item}")


def validate_rows(
    matrix: dict,
    symbols: list[str],
    package_root: pathlib.Path,
) -> tuple[list[tuple[dict, list[str]]], Counter]:
    rows = matrix.get("capabilities")
    if not isinstance(rows, list) or not rows:
        fail("matrix must define a non-empty capabilities list")
    tracking_values = matrix.get("tracking_specs")
    if not isinstance(tracking_values, list) or any(
        not isinstance(value, str) or not value for value in tracking_values
    ):
        fail("matrix must define its non-empty future Spec names")
    tracking_specs = set(tracking_values)
    if len(tracking_specs) != len(tracking_values):
        fail("matrix future Spec names must be unique")
    seen_ids: set[str] = set()
    ownership: dict[str, list[str]] = {symbol: [] for symbol in symbols}
    expanded: list[tuple[dict, list[str]]] = []
    status_counts: Counter = Counter()
    for row in rows:
        if not isinstance(row, dict):
            fail("every capability row must be an object")
        for field in ("id", "domain", "capability", "status", "patterns", "silex_contract"):
            if not isinstance(row.get(field), str) and field != "patterns":
                fail(f"capability row has invalid {field!r}: {row!r}")
        row_id = row["id"]
        if row_id in seen_ids:
            fail(f"duplicate capability id: {row_id}")
        seen_ids.add(row_id)
        if row["status"] not in STATUSES:
            fail(f"{row_id}: unknown status {row['status']!r}")
        if not row["domain"] or not row["capability"] or not row["silex_contract"]:
            fail(f"{row_id}: domain, capability and Silex contract must be non-empty")
        patterns = row["patterns"]
        if not isinstance(patterns, list) or not patterns:
            fail(f"{row_id}: patterns must be a non-empty list")
        matched: set[str] = set()
        for expression in patterns:
            if not isinstance(expression, str):
                fail(f"{row_id}: pattern must be a string")
            try:
                pattern = re.compile(expression)
            except re.error as error:
                fail(f"{row_id}: invalid pattern {expression!r}: {error}")
            current = {symbol for symbol in symbols if pattern.fullmatch(symbol)}
            if not current:
                fail(f"{row_id}: pattern matches no pinned symbol: {expression}")
            matched.update(current)
        for symbol in matched:
            ownership[symbol].append(row_id)
        validate_evidence(package_root, tracking_specs, row)
        expanded.append((row, sorted(matched)))
        status_counts[row["status"]] += 1

    missing = sorted(symbol for symbol, owners in ownership.items() if not owners)
    ambiguous = sorted(symbol for symbol, owners in ownership.items() if len(owners) > 1)
    if missing:
        fail(f"unclassified Box2D symbols: {', '.join(missing)}")
    if ambiguous:
        details = "; ".join(f"{symbol}: {ownership[symbol]}" for symbol in ambiguous)
        fail(f"multiply classified Box2D symbols: {details}")
    return expanded, status_counts


def write_report(
    path: pathlib.Path,
    matrix: dict,
    expanded: list[tuple[dict, list[str]]],
    symbol_count: int,
) -> None:
    lines = [
        "# Expanded Box2D 3.1.1 completeness matrix",
        "",
        "> Generated by `CheckCompleteness.py`; edit `CompletenessMatrix.json`.",
        "",
        f"Pinned revision: `{matrix['upstream']['revision']}`. Classified symbols: {symbol_count}.",
        "",
        "| Domain | Capability | Status | Box2D symbols | Evidence or tracking |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row, symbols in expanded:
        support = ", ".join(f"`{item}`" for item in row.get("evidence", []))
        if row.get("tracking"):
            support = f"{support}; {row['tracking']}" if support else row["tracking"]
        lines.append(
            f"| {row['domain']} | {row['capability']} | `{row['status']}` | "
            f"{', '.join(f'`{symbol}`' for symbol in symbols)} | {support} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--box2d-source", required=True, type=pathlib.Path)
    parser.add_argument(
        "--matrix",
        type=pathlib.Path,
        default=pathlib.Path(__file__).with_name("CompletenessMatrix.json"),
    )
    parser.add_argument("--report", type=pathlib.Path)
    parser.add_argument(
        "--final",
        action="store_true",
        help="reject every partial or planned gameplay capability",
    )
    arguments = parser.parse_args()

    try:
        matrix = load_matrix(arguments.matrix)
        upstream = matrix.get("upstream")
        if not isinstance(upstream, dict):
            fail("matrix must define upstream metadata")
        actual_revision = box2d_revision(arguments.box2d_source)
        actual_version = box2d_version(arguments.box2d_source)
        if actual_revision != upstream.get("revision"):
            fail(f"Box2D revision is {actual_revision}, expected {upstream.get('revision')}")
        if actual_version != upstream.get("version"):
            fail(f"Box2D version is {actual_version}, expected {upstream.get('version')}")

        by_header, symbols = public_symbols(arguments.box2d_source)
        expected_headers = upstream.get("headers")
        actual_headers = {name: len(values) for name, values in by_header.items()}
        if actual_headers != expected_headers:
            fail(f"public header inventory changed: {actual_headers}, expected {expected_headers}")
        if len(symbols) != upstream.get("symbol_count"):
            fail(f"found {len(symbols)} public symbols, expected {upstream.get('symbol_count')}")

        package_root = pathlib.Path(__file__).resolve().parents[2]
        expanded, status_counts = validate_rows(matrix, symbols, package_root)
        if arguments.final:
            incomplete = status_counts["partial"] + status_counts["planned"]
            if incomplete:
                fail(
                    "final matrix retains "
                    f"partial={status_counts['partial']} planned={status_counts['planned']}"
                )
        if arguments.report is not None:
            write_report(arguments.report, matrix, expanded, len(symbols))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"completeness validation failed: {error}", file=sys.stderr)
        return 1

    summary = " ".join(f"{status}={status_counts[status]}" for status in sorted(status_counts))
    print(f"completeness matrix classified {len(symbols)} Box2D symbols ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
