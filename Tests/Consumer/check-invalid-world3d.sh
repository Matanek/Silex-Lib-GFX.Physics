#!/usr/bin/env sh
set -eu

world3d_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
world3d_failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-world3d.XXXXXX")
world3d_binary="$PWD/.silex/physics3d-invalid-world"
trap 'rm -f "$world3d_failure_output" "$world3d_binary"' EXIT
silex compile "$world3d_consumer_root/Smokes/InvalidWorld3D.sx" \
    --debug --output "$world3d_binary"

check_failure() {
    world3d_case=$1
    world3d_message=$2
    if "$world3d_binary" "$world3d_case" \
        >"$world3d_failure_output" 2>&1
    then
        echo "$world3d_case unexpectedly accepted invalid World3D input" >&2
        exit 1
    fi
    grep -F "$world3d_message" "$world3d_failure_output" >/dev/null
}

check_failure gravity "GFX.Physics.World3D requires finite gravity"
check_failure density "GFX.Physics.RigidBody3DSettings requires finite motion, density and damping"
check_failure mass "GFX.Physics.RigidBody3D dynamic mass and principal inertia must be positive"
check_failure fixed-velocity "GFX.Physics.RigidBody3DSettings fixed body requires zero velocity"
check_failure kinematic-mass "GFX.Physics.RigidBody3DSettings mass override requires a dynamic body"
check_failure friction "GFX.Physics.RigidBody3D material requires finite non-negative friction and restitution in [0, 1]"
check_failure restitution "GFX.Physics.RigidBody3D material requires finite non-negative friction and restitution in [0, 1]"
check_failure material-mutation "GFX.Physics.RigidBody3D material requires finite non-negative friction and restitution in [0, 1]"
check_failure delta "GFX.Physics.World3D.step requires a finite non-negative delta"
check_failure impulse "GFX.Physics.RigidBody3D requires finite impulse"
check_failure stale "GFX.Physics.RigidBody3D no longer refers to a live body"
check_failure orphan "GFX.Physics.RigidBody3D no longer refers to a live body"
check_failure foreign "GFX.Physics.World3D cannot destroy a body owned by another world"
check_failure fixed "GFX.Physics.RigidBody3D force and impulse require a dynamic body"
check_failure duration "GFX.Physics.RigidBody3D kinematic duration must be finite and positive"
