#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
invalid_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-collider.XXXXXX")
trap 'rm -f "$invalid_output"' EXIT

if silex run "$physics_consumer_root/Smokes/InvalidChainMaterials.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid chain material cardinality unexpectedly succeeded" >&2
    exit 1
fi

grep -F "segment material count must match the chain segment count" \
    "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/InvalidDynamicChainCollider.sx" \
    >"$invalid_output" 2>&1
then
    echo "dynamic chain collider unexpectedly succeeded" >&2
    exit 1
fi

grep -F "chain colliders to belong to fixed bodies" \
    "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/StaleColliderHandle.sx" \
    >"$invalid_output" 2>&1
then
    echo "stale collider handle unexpectedly remained usable" >&2
    exit 1
fi

grep -F "Collider2D no longer refers to a live collider" \
    "$invalid_output" >/dev/null
