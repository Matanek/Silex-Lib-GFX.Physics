# Assemble two bodies rigidly

`World3D.create_fixed_constraint` preserves the relative position and
orientation of two bodies. Without explicit settings, the attachment captures
their current pose: a beam, its load and a moving support can form an assembly.
At least one body must be dynamic; both must be distinct and belong to the same
world.

This 2 kg load, offset by 2 m, stays suspended. Reattaching it later captures
its position after a fall:

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var support = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..transform = Physics.Transform3D(Math.Vec3(2.0,0.0,0.0))
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var attachment = world.create_fixed_constraint(support,weight)
    var step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(attachment.anchor_error().length() < 0.001)
    assert(attachment.angular_error().length() < 0.001)
    assert(Math.abs(attachment.reaction_force().y-19.62) < 0.05)
    assert(Math.abs(attachment.reaction_torque().z-39.24) < 0.1)
    world.destroy_fixed_constraint(attachment)
    step = 0
    while step < 30 { world.step(1.0 / 60.0); step++ }
    assert(!attachment.is_valid() && weight.position().y < -1.0)
    let captured = weight.transform()
    attachment = world.create_fixed_constraint(support,weight)
    step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(weight.position().nearly_equal(captured.position,0.001))
    assert(world.fixed_constraint_count() == 1)
    print("Fixed attachment: support, detach and current-pose reattachment verified")
}
```

The supporting force is 19.62 N and the torque is 39.24 Nm about Z. Destroying
the attachment releases the load; creating a new attachment without settings
fixes the new relative pose. Reattachment does not automatically return the
load to its old position.

## Choose and change the frames

`FixedConstraint3DSettings.first_local_frame` and `second_local_frame` are
`Transform3D` values, identity by default. With explicit settings, their origins
and orientations must coincide in world space. Positions are relative to body
origins, independently of the center of mass; rotations are local, unit and
finite. `Transform3D` rejects an invalid pose.

`first_local_frame()` and `second_local_frame()` return copies.
`set_frames(first, second)` replaces both frames atomically, clears previous
reactions and wakes the bodies. An initial pose far from the target is corrected
progressively during steps; creation does not teleport the bodies.

## Measure the assembly

`anchor_error()` is the world vector from the first anchor to the second.
`angular_error()` is the world rotation vector from the first frame to the
second: its direction is the signed axis and its length is the shortest angle
in radians, within `[0, pi]`. At pi, the axis may change sign without changing
the pose.

`reaction_force()` and `reaction_torque()` give the effort applied to the second
body during the last step, in world-space N and Nm; the first receives the
opposite effort. Torque is the attachment’s pure angular effort: the anchor
force’s moment about the center of mass adds to it. Reactions are solver
observations, including error correction; they are not a breakage limit. A zero
step preserves observations.

## Suspend or destroy the attachment

`set_enabled(false)` suspends effort without destroying the handle; reenabling
it resumes correction toward the existing frames. Every attachment mutation
wakes the bodies and resets its reactions. A disabled body also suspends effort.
Attachments share contacts and sleep islands in the [3D world](World3D.md).

`destroy_fixed_constraint()` or destruction of a linked body invalidates the
handle. `is_valid()` remains usable afterward; other operations reject stale
handles, including after slot reuse or world destruction.
`fixed_constraint_count()` counts live attachments, enabled or disabled.

The `Silex-Examples/Sources/Physics3D/FixedScene.sx` scene shows a translating
and rotating support, a beam and two loads. `D` detaches the blue load, `C`
reattaches it at its current pose, `M` stops the support, `I` applies an impulse,
`R` resets and Space pauses.
