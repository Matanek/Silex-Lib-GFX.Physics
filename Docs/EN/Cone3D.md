# 3D cone joint

`World3D.create_cone_constraint` keeps two anchors together and bounds the
inclination between two axes. Bodies can freely twist about their axes and
swing inside the cone.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var support = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var joint = world.create_cone_constraint(support,body,
        Physics.ConeConstraint3DSettings() ..half_angle = 0.4)
    body.set_angular_velocity(Math.Vec3(2.0,0.0,0.0))
    var i = 0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.angle()-0.4)<0.002 && joint.anchor_error().length()<0.001)
    joint.set_half_angle(0.2)
    i = 0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.angle()-0.2)<0.002)
    world.destroy_cone_constraint(joint);assert(!joint.is_valid())
    print("cone recipe: ok")
}
```

## Frames, limit and reactions

Anchors and axes are local to each body's shape frame, as used by
`Transform3D.point` and `Transform3D.vector`, rather than its center of mass.
For a world-space attachment, use `body.transform().inverse_point(point)` and
`inverse_vector(axis)` for each body. Finite nonzero axes are normalized.
Defaults are the origin, Z and a π/4 half-angle. `half_angle` lies in [0, π]
radians: 0 aligns the axes while leaving twist free; π does not restrict
orientation. `angle()` returns unsigned inclination in [0, π].

`anchor_error()` is the vector from the first anchor to the second in meters.
`reaction_force()` is the world-space force on the second body in N.
`reaction_torque()` is the free limit torque on that body in N·m; it excludes
the moment of the anchor force. Reactions describe the last positive step;
a zero step preserves them. This cone family has no motor, friction or spring.

## Mutation and lifetime

`set_anchors`, `set_axes`, `set_half_angle` and `set_enabled` clear reactions
and wake the linked bodies. Disabling the joint or either body suspends solving;
removing either body or the world invalidates the handle. Use
`World3D.destroy_cone_constraint` to remove it explicitly. Creation requires
two distinct bodies from the same world, with at least one dynamic body.
Check `is_valid()` before reusing a potentially stale handle; other operations
on stale handles fail explicitly.

## Qualification

The consumer and pinned Jolt witness cover free twist, swing stops in both
directions, load, half-angle mutation, unequal masses, an offset anchor at rest
and a rotated global frame. Further tests cover opposite axes, sleep, contacts
and destruction. Position correction is iterative; these witnesses do not
establish general spatial-chain behavior or exact impact-step reaction parity.
