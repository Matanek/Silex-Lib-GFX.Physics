#!/usr/bin/env python3
"""Validate the oracle worker adapter on a real deterministic world."""
import math
import subprocess
import sys

FIELDS = ("centroid_x", "centroid_y", "max_speed", "min_y", "max_overlap_mm",
          "awake", "contacts", "state_signature")


def values(line):
    return dict(field.split("=", 1) for field in line.split()[1:])


def main(binary):
    reference = None
    for workers in (1, 2, 4):
        for repeat in range(3):
            result = subprocess.run([binary, "--release-parity", f"--workers-{workers}", "--task-stats"],
                                    check=True, capture_output=True, text=True, timeout=30)
            rows = result.stdout.splitlines()
            assert len(rows) == 1 and rows[0].startswith("SILEX_PHYSICS_CORPUS ")
            data = values(rows[0])
            assert data["workers"] == str(workers)
            observed = tuple(data[field] for field in FIELDS)
            assert all(math.isfinite(float(value)) for value in observed)
            if reference is None: reference = observed
            assert observed == reference, (workers, repeat, observed, reference)
            lines = [line for line in result.stderr.splitlines() if line.startswith("ORACLE_TASKS ")]
            assert len(lines) == 1
            stats = values(lines[0])
            assert stats["workers"] == str(workers)
            assert int(stats["groups"]) > 0 and stats["groups"] == stats["finished"]
            assert int(stats["items"]) > 0 and stats["items"] == stats["completed"]
            assert int(stats["mask"]) == (1 << workers) - 1
    for flags in (("--workers-2", "--workers-4"), ("--workers-8",), ("--substeps-2", "--substeps-4")):
        result = subprocess.run([binary, "--release-parity", *flags], capture_output=True, timeout=30)
        assert result.returncode == 2
    print("9 real-world runs preserve state, complete all work and activate every configured worker")


if __name__ == "__main__":
    main(sys.argv[1])
