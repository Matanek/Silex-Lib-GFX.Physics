#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
stale_handle_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-stale-handle.XXXXXX")
trap 'rm -f "$stale_handle_output"' EXIT

if silex run "$physics_consumer_root/Smokes/StaleBodyHandle.sx" \
    >"$stale_handle_output" 2>&1
then
    echo "stale body handle unexpectedly remained usable" >&2
    exit 1
fi

grep -F "GFX.Physics.RigidBody2D no longer refers to a live body" \
    "$stale_handle_output" >/dev/null
