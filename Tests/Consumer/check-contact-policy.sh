#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
policy_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-contact-policy.XXXXXX")
trap 'rm -f "$policy_output"' EXIT

if silex run "$physics_consumer_root/Smokes/InvalidContactDecision.sx" \
    >"$policy_output" 2>&1
then
    echo "invalid contact decision unexpectedly succeeded" >&2
    exit 1
fi

grep -F "manifold normal must have unit length" "$policy_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/ReentrantContactPolicy.sx" \
    >"$policy_output" 2>&1
then
    echo "reentrant contact policy unexpectedly mutated the world" >&2
    exit 1
fi

grep -F "cannot be mutated during step" "$policy_output" >/dev/null
