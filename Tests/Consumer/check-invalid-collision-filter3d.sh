#!/usr/bin/env sh
set -eu

consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZIG_GLOBAL_CACHE_DIR="$PWD/.silex/zig"
export ZIG_GLOBAL_CACHE_DIR
failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-filter3d.XXXXXX")
trap 'rm -f "$failure_output"' EXIT

for mode in debug release; do
    binary="$PWD/.silex/physics3d-invalid-filter-$mode"
    trap 'rm -f "$failure_output" "$binary"' EXIT
    silex compile "$consumer_root/Smokes/InvalidCollisionFilter3D.sx" \
        "--$mode" --output "$binary"
    if "$binary" >"$failure_output" 2>&1; then
        echo "zero category unexpectedly accepted" >&2
        exit 1
    fi
    grep -F "CollisionFilter3D requires at least one category bit" \
        "$failure_output" >/dev/null
    rm -f "$binary"
done
echo "zero collision category rejected in Debug and Release"
