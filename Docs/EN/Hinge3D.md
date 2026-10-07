# Connect two bodies around a rotation axis

`World3D.create_hinge_constraint` holds two attachment points together and
aligns their axes while allowing rotation around that axis. Hard stops bound
this rotation. The hinge participates in the contacts and sleep islands of
the [3D world](World3D.md).

This pendulum rotates in the XY plane and stays attached to its fixed support:

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.1)))
    let rotation = Math.Quat.angle_axis(0.4,Math.Vec3(0.0,0.0,1.0))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.25))
        ..transform = Physics.Transform3D(rotation.rotate(Math.Vec3(0.0,-1.0,0.0)),rotation)
        ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,weight,Physics.HingeConstraint3DSettings()
        ..second_local_anchor = Math.Vec3(0.0,1.0,0.0)
        ..minimum_angle = -0.5 ..maximum_angle = 0.5)
    var step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(hinge.anchor_error().length() < 0.005)
    assert(hinge.axis_error() < 0.001)
    print("Pendulum angle: $(hinge.angle()) rad")
}
```

## Define the axis and zero angle

Anchors are points in the bodies' local frames, independent of their centers
of mass. `first_local_axis` and `second_local_axis` define the rotation axis;
both default to Z. `first_local_normal` and `second_local_normal` define the
direction corresponding to zero angle; both default to X. Each normal must
be independent of its axis. Creation normalizes the axis and projects the
normal into its perpendicular plane. Vectors and their squared lengths must
be finite, nonzero and not nearly collinear.

`angle()` measures the signed rotation of the second frame relative to the
first using the right-hand rule around the first axis, in `[-pi, pi]`.
`axis_error()` measures the angle between the axes in radians;
`anchor_error()` is the vector from the first world anchor to the second.
The angle is useful when the axes are aligned; correcting a strongly
misaligned initial pose may take several steps. To treat an initial rotation
as zero, express the two local normals so they coincide in world space.

## Change stops and frames

`minimum_angle` and `maximum_angle` are finite, ordered radians within
`[-pi, pi]`. Defaults disable the stops; equal values lock the angle.
Stops are rigid, with no imposed bounce or friction on the free axis. They
are resolved at each simulation step; they do not continuously detect every
rotation.

`set_limits(minimum, maximum)`, `set_anchors(first, second)` and
`set_frames(first_axis, first_normal, second_axis, second_normal)` modify the
live hinge. `set_enabled(false)` suspends its reactions without destroying
its handle; `set_enabled(true)` reactivates it. Every mutation wakes the
linked bodies and clears stored reactions.

## Request a speed with a maximum torque

`HingeMotor3D(speed, maximum_torque)` describes a relative speed in rad/s and
a symmetric torque limit. Set `settings.motor` during creation or replace it
with `set_motor(...)` at runtime. This example reaches its target, reverses,
then turns the motor off:

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var wheel = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,wheel,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D(speed:1.0,maximum_torque:0.2))
    var step = 0
    while step < 60 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(hinge.angular_speed()-1.0) < 0.0001)
    hinge.set_motor(Physics.HingeMotor3D(speed:-1.0,maximum_torque:0.2))
    step = 0
    while step < 90 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(hinge.angular_speed()+1.0) < 0.0001)
    hinge.set_motor(null)
    assert(hinge.motor() == null && hinge.motor_torque() == 0.0)
    print("Hinge motor: target, reversal and off verified")
}
```

`speed` follows the sign of `angle()`. `angular_speed()` measures the second
body’s speed relative to the first, projected onto the first world axis.
Both parameters must be finite; `maximum_torque` must be nonnegative.
Zero torque supplies no effort. A zero target brakes rotation, while
`set_motor(null)` leaves the axis free and preserves its current speed.
`motor()` returns the current optional configuration. A copy of that value
is independent of later mutations to the hinge.

`motor_torque()` measures the signed motor torque during the last positive
step, in N·m with kilograms, meters and seconds. It stays within its limit
regardless of iteration count or step duration. Anchor and stop reactions can
exceed that limit: it bounds the motor’s effort. A stop can therefore arrest
the body despite the target; the motor keeps pushing and the stop reaction
can cancel its torque. The target requests available effort and is not a
guarantee that the speed will be reached under excessive load.

Mutations clear observations and wake the linked bodies. An active motor
with nonzero speed and available torque keeps its bodies awake; a zero target
can let them sleep once stopped. Disabling the hinge or either body suspends
the motor. `step(0)` preserves its observation. Joints in a world containing
an active powered motor are prepared after forces and before movement, then
solved with contacts; the effort limit is shared between those phases.

## Read reactions and manage lifetime

`reaction_force()` gives the world force applied to the second body at its
anchor during the last positive step. `reaction_torque()` gives the world
angular torque applied to the second body by the motor, axis alignment and
stops. It excludes the moment of the anchor force around the center of mass.
Units are mass × distance / second² and mass × distance² / second²; with
kilograms, meters and seconds these are newtons and N·m. `step(0)` preserves
observations; an inactive hinge reports zero reaction after the next positive
step, or immediately after explicit deactivation.

Both bodies must be distinct, live and owned by the same world; at least one
must be dynamic. Their mutual collisions remain active. Use body filters if
their shapes overlap around the pivot. Disabling a body also suspends its
hinge resolution.

`destroy_hinge_constraint(hinge)` invalidates every copy of the handle.
Destroying a linked body or the world also invalidates them; check with
`is_valid()`. `first_body()` and `second_body()` retrieve the linked bodies,
and `hinge_constraint_count()` counts only live hinges.

Qualification covers pendulums, mutated stops, an unequal-mass chain and
terrain contacts on macOS ARM64 Native Debug/Release. The velocity motor is
qualified by analytical acceleration, inertia about the pivot, reversal,
motor off, stops, a chain and contacts.
[Position control](HingePosition3D.md) and
[axis friction](HingeFriction3D.md) are available. Soft stops remain to be
implemented.

[Signed torque bounds](HingeTorqueBounds3D.md) permit different effort in each direction, in velocity or position mode.
