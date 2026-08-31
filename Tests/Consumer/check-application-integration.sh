#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
invalid_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-application.XXXXXX")
trap 'rm -f "$invalid_output"' EXIT

if silex run "$physics_consumer_root/Smokes/InvalidPhysics2DDelta.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid Physics2D fixed delta unexpectedly succeeded" >&2
    exit 1
fi
grep -F "fixed delta must be finite and positive" "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/InvalidPhysics2DWorkers.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid Physics2D worker count unexpectedly succeeded" >&2
    exit 1
fi
grep -F "worker count must be positive" "$invalid_output" >/dev/null
