# 3D slider

A `SliderConstraint3D` guides a body along the first body's rail. The X axes
of its two local frames define the free translation; their Y/Z axes and
relative orientation stay aligned. The rail may belong to a fixed, kinematic
or dynamic body. At least one of the two bodies must be dynamic.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0)
        ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings()
        ..minimum_position = -0.5 ..maximum_position = 0.75)
    carriage.set_linear_velocity(Math.Vec3(0.5, 0.0, 0.0))
    var step = 0
    while step < 60 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(joint.position() - 0.5) < 0.0001)
    assert(joint.anchor_error().length() < 0.0001)
    assert(joint.angular_error().length() < 0.0001)
    assert(Math.abs(joint.reaction_force().y - 19.62) < 0.0001)
}
```

`first_local_frame` and `second_local_frame` use each body's public transform,
before its center of mass offset. Both default to `Transform3D()`; these
frames require matching orientations and allow displacement along X. Rotate
the local frames or the supporting body to orient the rail. Rotation of the
first body carries the rail and the carriage's velocity.

`position()` returns the frame separation projected onto the first frame's
X axis, in meters. `speed()` is its signed derivative in m/s, including rail
translation and rotation. `anchor_error()` returns only the world transverse
error: free travel is not an error. `angular_error()` is the world rotation
vector separating the frames in radians, using the short path.

`minimum_position` and `maximum_position` are optional signed bounds. `null`
opens that side; two bounds must be finite and ordered. They may be equal,
even away from zero, locking the last degree of freedom when `limit_spring`
is `null`. Pinned Jolt rejects equal rigid slider bounds; this Silex case is
compared to the equivalent Jolt fixed attachment.
By default, stops are rigid
and unilateral: they oppose outgoing velocity and allow inward motion.

`reaction_force()` and `reaction_torque()` return the world force in N and
world reaction torque in N·m applied to the second body during the last
positive step. The torque is the free couple holding orientation; add the
anchor force's moment for the total effort about the center of mass.
`limit_force()` isolates the signed axial stop force, positive at the lower
bound and negative at the upper bound. Equal bounds allow either sign.
`step(0.0)` preserves the latest measurements.

`set_frames(first, second)`, `set_limits(minimum, maximum)` and
`set_enabled(enabled)` update the constraint, clear its reactions and wake
both bodies. Frame reads return values; changing the settings used at creation
does not update the slider. Disabling a body suspends the constraint and
clears its measurements on the next positive step. Mass and pose changes
take effect on that step.

`World3D.slider_constraint_count()` counts live sliders.
`destroy_slider_constraint(joint)` invalidates all its references; destroying
a connected body or dropping the world also invalidates them. `is_valid()`
remains readable; other calls through stale references are rejected.
Constraints participate in real contacts and sleeping islands.

Free travel and rigid stops can be combined with the
[velocity motor](SliderMotor3D.md) or [position servo](SliderPosition3D.md).
[Axial friction](SliderFriction3D.md) adds a passive brake; a
[stop spring](SliderSoftLimits3D.md) allows temporary compression.
Jolt fixtures cover translation,
loaded stop reactions, offset frames and rotating rails; parity for impact
transients and general spatial chains has not been established.
`SliderScene.sx` shows an inclined rail, gravity and a launch impulse with T;
R resets, Space pauses/resumes and Escape closes the window.

[Signed force bounds](SliderForceBounds3D.md) set different effort in each direction, in velocity and position modes.

[Soft slider stops](SliderSoftLimits3D.md): load compression, damped spring, equal bounds and mutation.
