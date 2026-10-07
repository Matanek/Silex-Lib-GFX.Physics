# 3D path guidance

`World3D.create_path_constraint` guides a body's anchor along a path carried
by another body. Distance, targets and speeds use meters and m/s. The immutable
path may be open or closed. Two normal directions are constrained; its tangent
remains free or receives a motor, friction and open endpoint stops.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var carrier=world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type=Physics.BodyType3D.fixed
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var carriage=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var route=Physics.Path3D.line(Math.Vec3(),Math.Vec3(10.0,0.0,0.0),Math.Vec3(0.0,1.0,0.0))
    var guide=world.create_path_constraint(carrier,carriage,Physics.PathConstraint3DSettings(route)
        ..orientation=Physics.PathOrientation3D.follow_path
        ..motor=Physics.LinearMotor3D.position(3.0,20.0,40.0,12.0))
    var step=0;while step<300 { world.step(1.0/60.0);step++ }
    assert(Math.abs(guide.position()-3.0)<0.001 && guide.anchor_error().length()<0.001)
    guide.set_motor(Physics.LinearMotor3D(1.0,12.0));world.step(1.0/60.0)
    assert(guide.speed()>0.0 && guide.motor_force()<=12.001)
    guide.set_motor(null);guide.set_maximum_friction_force(6.0)
    step=0;while step<60 { world.step(1.0/60.0);step++ }
    assert(Math.abs(guide.speed())<0.001)
    world.destroy_path_constraint(guide);assert(!guide.is_valid())
    print("path recipe: ok")
}
```

## Geometry and frames

`PathKnot3D(position, tangent, normal)` describes a Hermite knot. Tangent
magnitude shapes each segment. The normal is projected perpendicular to the
tangent and normalized. `Path3D(knots, closed=false)` owns its knot array:
at least two knots for an open path, three for a loop. Coefficients, lengths
and projections must be finite and representable. Every segment must retain
a nonzero tangent and an independent normal over its entire interval. Shared
knot tangents and normals make the frame continuous. Cusps, a collapsed blended
normal, degenerate or numerically too small segments fail explicitly.

`Path3D.line(start, end, normal)` builds a straight Hermite path. Observe it
through `length`, `is_closed`, `knot_count` and `knot`. `frame(distance)` returns
a path-local `Transform3D` with X tangent, Y normal and Z binormal (X × Y = Z).
Open distances clamp to endpoints; closed distances wrap, and must remain finite
and representable relative to path length. Arc tables are prepared at creation;
queries invert physical distance without exposing fractional segment indices.

`closest_position(point, hint=0.0)` returns the nearest arc distance in meters.
It checks all segment stationary roots and endpoints. The hint breaks equal
distance ties, including intersections; it cannot force a more distant branch.
Blended normals are reorthogonalized along each segment.

`PathConstraint3DSettings(path)` requires the path. `first_local_path_frame`
is relative to the first body's shape frame, identity by default.
`second_local_anchor` is local to the second body, zero by default. Creation
captures the current position and orientation reference. The carrier may be
fixed, kinematic or dynamic.

## Drives and orientation

`motor: LinearMotor3D?` reuses velocity, position and position/velocity commands,
signed force limits in N, stiffness in N/m and damping in N·s/m. Open targets
clamp to endpoints; loop targets use the shortest signed arc error.
`maximum_friction_force` passively brakes in N while the motor is absent.
A nonzero velocity combined with a fixed position target creates the discrete
equilibrium target + speed × (damping + dt × stiffness) / stiffness; it does
not advance the target automatically.

`PathOrientation3D` supports `free`, `around_tangent`, `around_normal`,
`around_binormal`, `follow_path` and `relative_to_body`. Around-axis modes keep
one free rotation and follow the other two directions. `follow_path` preserves
the captured path-relative orientation; `relative_to_body` preserves the
carrier-relative orientation. The analytic frame derivative supplies angular
velocity from curvature and normal twist. Its reactions exchange linear impulse
and torque with the corresponding effective inertia. Guidance is locally
linearized per step: use a sufficiently small timestep for direction and normal
changes.

## Observations and mutation

`position()` measures current arc distance; `speed()` measures relative anchor
speed along its tangent. `anchor_error()` is the world vector from the nearest
path point to the anchor, including longitudinal endpoint overshoot.
`reaction_force()` gives world force on the second body. `reaction_torque()`
gives its free orientation couple in N·m, excluding the anchor lever moment.
`motor_force()` and `friction_force()` separate signed tangent efforts. Reactions
record the last positive step; a zero step preserves them. Pose correction does
not change velocities.

`set_path`, `set_frames` and `set_orientation` recapture the orientation reference
from current poses. `set_motor`, `set_maximum_friction_force` and `set_enabled`
retain it. Every mutation clears reactions and wakes the bodies. Corresponding
getters support inspection. Disabling a body or constraint suspends resolution.

Bodies must be distinct, belong to the same world, and include a dynamic body.
`path_constraint_count` counts live constraints; `destroy_path_constraint`
destroys one. Destroying a body or world invalidates retained handles; generations
prevent slot reuse from reviving them. `is_valid` remains callable after
destruction; other stale operations fail explicitly.

## Qualification and reference boundaries

Debug/Release Jolt witnesses cover a straight guide, speed, position and combined
drives on a one-meter line, friction, five orientations, a rotated frame and a
free-orientation loop. Independent tests cover drives over different line lengths,
curved and spatial-normal transport, effective inertia, power, contacts and safety.

Pinned Jolt uses a segment fraction as the position motor error, changing spring
scale on a two-meter segment. Its curved follow mode also corrects orientation
without including the frame derivative in angular velocity. Both differences are
retained as explicit witnesses; physical tests remain independent of those gaps.
General spatial chains and exact impact phase require separate qualification.
