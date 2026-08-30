#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
invalid_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-world.XXXXXX")
trap 'rm -f "$invalid_output"' EXIT

if silex run "$physics_consumer_root/Smokes/InvalidWorldSettings.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid maximum linear speed unexpectedly succeeded" >&2
    exit 1
fi
grep -F "maximum linear speed must be finite and positive" \
    "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/InvalidWorldTuning.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid contact tuning unexpectedly succeeded" >&2
    exit 1
fi
grep -F "contact stiffness must be finite and non-negative" \
    "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/InvalidWorldSubsteps.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid substep count unexpectedly succeeded" >&2
    exit 1
fi
grep -F "requires a positive substep count" "$invalid_output" >/dev/null

if silex run "$physics_consumer_root/Smokes/InvalidWorldFiniteValue.sx" \
    >"$invalid_output" 2>&1
then
    echo "non-finite world gravity unexpectedly succeeded" >&2
    exit 1
fi
grep -F "gravity must be finite" "$invalid_output" >/dev/null
