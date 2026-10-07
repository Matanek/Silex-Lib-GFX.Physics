# 3D slider position servo

`SliderMotor3D.position(position, maximum_force, stiffness, damping)` drives
a carriage toward signed relative travel. The target is in metres along X of
the first frame, symmetric capacity in N, stiffness in N/m and damping in
N·s/m. The [velocity motor](SliderMotor3D.md) remains available.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0)
        ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings() ..minimum_position = -1.0 ..maximum_position = 1.0
        ..motor = Physics.SliderMotor3D.position(0.75, 10.0, 8.0, 8.0))
    var step = 0
    while step < 720 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() - 0.75) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D.position(-0.4, 10.0, 8.0, 8.0))
    step = 0
    while step < 720 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() + 0.4) < 0.0001)
    assert(joint.motor()!.target_position == -0.4)
    joint.set_motor(null)
    assert(joint.motor_force() == 0.0)
}
```

All four values must be finite; stiffness is strictly positive, damping and
maximum force are nonnegative. Zero damping permits oscillation; zero capacity
leaves travel free. `target_position`, `maximum_force`, `stiffness` and `damping`
are readable command values; `speed` is zero in position mode. In velocity mode,
`target_position` is `null` and stiffness/damping are zero.

`joint.set_motor(...)` changes the target or switches between position,
velocity and `null`, clears reactions and wakes both bodies. `joint.motor()`
retains the requested target; the effective target is projected between active
limits. An outside target therefore does not demand a permanent force against
a stop. Restraints, real contacts and [slider](Slider3D.md) lifetime rules
remain active. Capacity bounds accumulated motor force over the entire step.

The spring and damper use physical units: a constant load produces an
equilibrium offset equal to its force divided by stiffness. Insufficient
capacity can let the carriage continue moving backward. `motor_force()`
reports the servo's signed effort; `reaction_force()` also includes restraints
and stops. The free couple can compensate an offset anchor. A position command
with positive capacity keeps the bodies awake, even with a zero target.
A zero step retains observations; suspension and destruction follow slider rules.

Consumers check the recurrence at 60/120 Hz, undamped oscillation, saturation,
load, reduced mass, offset 3D frames/COM, limits, mutations, sleep, suspension
and contacts. The Jolt oracle qualifies eight 60 Hz cases in Debug/Release:
critical/weak damping, saturation, successive modes, limited targets, load,
two free masses and an offset anchor. Impact, rotating-rail transient and general
spatial-chain parity remain unestablished. Combined position/velocity commands,
signed force bounds and soft stops remain to be qualified.

`SliderPositionScene.sx` compares a strongly damped gold carriage with an
oscillating blue carriage; green markers show the target. T reverses the target,
R resets, Space pauses/resumes and Escape quits.

The [slider friction brake](SliderFriction3D.md) slows travel without a motor using mutable maximum force.
