#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
invalid_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-character.XXXXXX")
trap 'rm -f "$invalid_output"' EXIT

if silex run "$physics_consumer_root/Smokes/InvalidCharacterMover.sx" \
    >"$invalid_output" 2>&1
then
    echo "invalid character mover settings unexpectedly succeeded" >&2
    exit 1
fi
grep -F "maximum iterations must be between 1 and 32" \
    "$invalid_output" >/dev/null
