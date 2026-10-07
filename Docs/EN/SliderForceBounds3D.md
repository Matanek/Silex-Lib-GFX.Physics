# 3D slider motor force bounds

`SliderMotor3D(speed, minimum_force, maximum_force)` pushes and brakes with
different effort in each direction. Speed is in m/s; signed bounds are in N
on the second body, with positive force increasing travel along X of the
first frame.

This carriage reaches +0.6 m/s quickly, then returns slowly toward −0.6 m/s
because negative braking is limited to −0.5 N.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings() ..motor = Physics.SliderMotor3D(0.6, -0.5, 2.0))
    var step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.6) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D(-0.6, -0.5, 2.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.35) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D.position(-0.4, -2.0, 8.0, 8.0, 8.0))
    step = 0
    while step < 960 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() + 0.4) < 0.001)
    assert(joint.motor()!.minimum_force == -2.0 && joint.motor()!.maximum_force == 8.0)
}
```

After one second of reversal, speed remains +0.35 m/s: a force bound limits
acceleration without forbidding an existing velocity. The final servo uses
signed bounds with 8 N/m stiffness and 8 N·s/m damping.

Existing `SliderMotor3D(speed, maximum_force)` and
`position(position, maximum_force, stiffness, damping)` remain symmetric:
`minimum_force == -maximum_force`. The new overload
`position(position, minimum_force, maximum_force, stiffness, damping)`
retains the [physical spring](SliderPosition3D.md). Command values are immutable
and `joint.motor()` returns an optional value snapshot.

Bounds must be finite and ordered. `maximum_force` denotes the signed upper
bound in these overloads. `[0, F]` pushes without pulling; `[-F, 0]` pulls
without pushing; `[0, 0]` leaves travel free. Excluding zero imposes effort
even at target speed or position. Equal bounds impose that constant force.
The accumulated budget is shared across the entire step, without being
repeated at each pass.

`set_motor(...)` replaces the command, clears reactions and wakes the bodies.
An installed motor still takes precedence over [axial friction](SliderFriction3D.md),
including at `[0, 0]`; `set_motor(null)` restores configured friction.
`motor_force()` reports signed effort; `reaction_force()` also includes
restraints and stops. A zero or negative upper bound remains active.
An interval excluding zero keeps bodies awake even at a zero target; a zero
interval permits sleep. A zero step retains observations; suspension,
destruction and frame/limit mutations follow [slider](Slider3D.md) rules.

Tests check 60/120 Hz recurrences, one-sided/equal/same-sign intervals,
servo, reduced mass, offset 3D COM/anchors, mutations, sleep, stops and real
contact. Eight Debug/Release Jolt trajectories additionally qualify both
traces against independent mechanics before comparison. Impact, rotating
transient and general spatial-chain parity remain unestablished; combined
commands and linear soft stops remain to be qualified.

`SliderForceBoundsScene.sx` compares a gold carriage using [-0.5, 2] N with
a blue carriage using symmetric ±2 N. T reverses target speed, R resets,
Space pauses/resumes and Escape quits. Gold reverses motion more slowly
when negative effort is required.
