#!/usr/bin/env sh
set -eu

consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZIG_GLOBAL_CACHE_DIR="$PWD/.silex/zig"
export ZIG_GLOBAL_CACHE_DIR
failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-continuous3d.XXXXXX")
trap 'rm -f "$failure_output"' EXIT

for mode in debug release; do
    binary="$PWD/.silex/physics3d-invalid-continuous-$mode"
    trap 'rm -f "$failure_output" "$binary"' EXIT
    silex compile "$consumer_root/Smokes/InvalidContinuous3D.sx" \
        "--$mode" --output "$binary"
    if "$binary" >"$failure_output" 2>&1; then
        echo "fixed continuous body unexpectedly accepted" >&2
        exit 1
    fi
    grep -F "continuous collision requires a dynamic body" \
        "$failure_output" >/dev/null
    rm -f "$binary"
done
echo "continuous collision rejects fixed bodies in Debug and Release"
