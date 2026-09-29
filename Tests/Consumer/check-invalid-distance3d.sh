#!/usr/bin/env sh
set -eu

consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ZIG_GLOBAL_CACHE_DIR="$PWD/.silex/zig"
export ZIG_GLOBAL_CACHE_DIR
failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-distance3d.XXXXXX")
trap 'rm -f "$failure_output"' EXIT

check_failure() {
    binary=$1
    case_name=$2
    message=$3
    if "$binary" "$case_name" >"$failure_output" 2>&1; then
        echo "$case_name unexpectedly accepted invalid DistanceConstraint3D input" >&2
        exit 1
    fi
    grep -F "$message" "$failure_output" >/dev/null
}

for mode in debug release; do
    binary="$PWD/.silex/physics3d-invalid-distance-$mode"
    trap 'rm -f "$failure_output" "$binary"' EXIT
    silex compile "$consumer_root/Smokes/InvalidDistanceConstraint3D.sx" \
        "--$mode" --output "$binary"
    check_failure "$binary" negative "requires finite ordered non-negative limits"
    check_failure "$binary" reversed "requires finite ordered non-negative limits"
    check_failure "$binary" anchor "requires finite local anchors"
    check_failure "$binary" same "requires two distinct bodies"
    check_failure "$binary" fixed-fixed "requires a dynamic body"
    check_failure "$binary" foreign "requires bodies from its world"
    check_failure "$binary" mutation "requires finite ordered non-negative limits"
    check_failure "$binary" stale "no longer refers to a live constraint"
    check_failure "$binary" foreign-destroy "cannot destroy a constraint owned by another world"
    check_failure "$binary" negative-hertz "requires finite non-negative spring frequency and damping ratio"
    check_failure "$binary" nan-damping "requires finite non-negative spring frequency and damping ratio"
    check_failure "$binary" negative-damping-mutation "requires finite non-negative spring frequency and damping ratio"
    rm -f "$binary"
done
echo "distance3d rejected 24 invalid creation and mutation cases"
