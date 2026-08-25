#!/usr/bin/env sh
set -eu

geometry_consumer_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
geometry_failure_output=$(mktemp "${TMPDIR:-/tmp}/gfx-physics-invalid-geometry.XXXXXX")
trap 'rm -f "$geometry_failure_output"' EXIT

check_failure() {
    geometry_source=$1
    geometry_message=$2
    if silex run "$geometry_consumer_root/Smokes/$geometry_source" \
        >"$geometry_failure_output" 2>&1
    then
        echo "$geometry_source unexpectedly accepted invalid geometry" >&2
        exit 1
    fi
    grep -F "$geometry_message" "$geometry_failure_output" >/dev/null
}

check_failure InvalidCircle.sx \
    "GFX.Physics.Circle2D requires a finite positive radius"
check_failure InvalidCapsule.sx \
    "GFX.Physics.Capsule2D requires two distinct endpoints"
check_failure InvalidPolygon.sx \
    "GFX.Physics.Polygon2D requires non-collinear points"
check_failure InvalidChain.sx \
    "GFX.Physics.Chain2D rejects consecutive duplicate points"
check_failure InvalidRay.sx \
    "GFX.Physics.Ray2D requires a non-zero translation"
