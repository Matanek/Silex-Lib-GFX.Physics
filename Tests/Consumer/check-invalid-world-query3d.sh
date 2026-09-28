#!/usr/bin/env sh
set -eu

consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZIG_GLOBAL_CACHE_DIR="$PWD/.silex/zig"
export ZIG_GLOBAL_CACHE_DIR
failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-world-query3d.XXXXXX")
trap 'rm -f "$failure_output"' EXIT

for mode in debug release; do
    binary="$PWD/.silex/physics3d-invalid-world-query-$mode"
    trap 'rm -f "$failure_output" "$binary"' EXIT
    silex compile "$consumer_root/Smokes/InvalidWorldQuery3D.sx" \
        "--$mode" --output "$binary"
    for case_name in foreign-ray foreign-overlap stale-ray stale-all; do
        if "$binary" "$case_name" >"$failure_output" 2>&1; then
            echo "$case_name unexpectedly accepted an invalid ignored body" >&2
            exit 1
        fi
        grep -F "query requires a live ignored body from this world" \
            "$failure_output" >/dev/null
    done
    rm -f "$binary"
done
echo "world queries rejected 8 foreign or stale ignored bodies"
