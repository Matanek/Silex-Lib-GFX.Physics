#!/usr/bin/env sh
set -eu

joint_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
joint_failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-joint-runtime.XXXXXX")
trap 'rm -f "$joint_failure_output"' EXIT

check_failure() {
    joint_source=$1
    joint_message=$2
    if silex run "$joint_consumer_root/Smokes/$joint_source" \
        >"$joint_failure_output" 2>&1
    then
        echo "$joint_source unexpectedly accepted invalid joint state" >&2
        exit 1
    fi
    grep -F "$joint_message" "$joint_failure_output" >/dev/null
}

check_failure InvalidJointLimits.sx \
    "GFX.Physics joint limits are invalid"
check_failure InvalidJointAxis.sx \
    "GFX.Physics joint axis must be finite and non-zero"
check_failure InvalidJointFiniteValue.sx \
    "GFX.Physics mouse joint settings are invalid"
check_failure StaleJointHandle.sx \
    "GFX.Physics joint handle no longer refers to a live joint"
