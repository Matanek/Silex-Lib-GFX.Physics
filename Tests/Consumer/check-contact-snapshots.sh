#!/usr/bin/env sh
set -eu

snapshot_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
snapshot_failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-contact-snapshot.XXXXXX")
trap 'rm -f "$snapshot_failure_output"' EXIT

if silex run "$snapshot_consumer_root/Smokes/StaleEventCollider.sx" \
    >"$snapshot_failure_output" 2>&1
then
    echo "stale event collider unexpectedly remained mutable" >&2
    exit 1
fi

grep -F "Collider2D no longer refers to a live collider" \
    "$snapshot_failure_output" >/dev/null
