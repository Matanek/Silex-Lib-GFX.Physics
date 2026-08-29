#!/usr/bin/env sh
set -eu

physics_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
body_control_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-body-control.XXXXXX")
trap 'rm -f "$body_control_output"' EXIT

check_failure() {
    body_control_source=$1
    body_control_message=$2
    if silex run "$physics_consumer_root/Smokes/$body_control_source" \
        >"$body_control_output" 2>&1
    then
        echo "$body_control_source unexpectedly accepted an invalid body action" >&2
        exit 1
    fi
    grep -F "$body_control_message" "$body_control_output" >/dev/null
}

check_failure FixedBodyForce.sx \
    "GFX.Physics.RigidBody2D physical actions require a dynamic body"
check_failure StaleBodyAction.sx \
    "GFX.Physics.RigidBody2D no longer refers to a live body"
