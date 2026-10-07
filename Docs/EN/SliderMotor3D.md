# 3D slider motor

`SliderMotor3D(speed, maximum_force)` drives a carriage toward a signed
relative speed with a symmetric force capacity. Speed is in m/s along
the first frame's X axis; capacity is in N. The rail can move and rotate.
The motor preserves the five degrees locked by the [slider](Slider3D.md).

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
        Physics.SliderConstraint3DSettings()
        ..motor = Physics.SliderMotor3D(0.6, 2.0))
    var step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.6) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D(0.0, 2.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001)
    joint.set_motor(null)
    assert(joint.motor() == null && joint.motor_force() == 0.0)
}
```

`speed` must be finite; `maximum_force` must be finite and nonnegative.
Capacity bounds the accumulated motor force over one step, regardless of
iteration count. The motor accelerates gradually toward its target: a load
above capacity can prevent the requested speed or move the carriage backward.
Zero capacity neither drives nor brakes the free axis.

`SliderConstraint3DSettings.motor` is optional. `null` leaves travel free;
a zero target speed brakes and holds the carriage with the same capacity.
`joint.motor()` returns an optional value describing the current command.
`set_motor(motor)` replaces it; `set_motor(null)` disables the drive while
preserving the slider's locked degrees and stops. Replacement clears
reactions and wakes both bodies.

`motor_force()` reports signed motor force in N on the second frame during
the last positive step, positive toward increasing travel. `reaction_force()`
includes the motor, stops and transverse restraints. `limit_force()` remains
the axial stop reaction alone. A motor pushing against a stop can supply
its capacity while the stop balances it: a zero total reaction does not mean
the motor is inactive. `reaction_torque()` remains the free orientation
couple; it can balance the moment of motor force at an offset anchor.

`step(0.0)` preserves the last observations. Changing frames, limits or
activation also clears the motor measurement. Suspending a body or the
constraint prevents driving and zeros its effort at the next positive step.
A nonzero target with positive capacity wakes the bodies; a zero target can
let a stationary assembly sleep. Slider destruction and stale-reference
rules also apply to its motor operations.

The consumer and Jolt oracle qualify acceleration, reversal, braking,
two free unequal masses, an offset anchor and loads above capacity.
The rotating rail is compared at steady constant relative speed. Parity
of force transitions while the rail rotates, impacts and general spatial
chains remains open. Signed force bounds
and soft stops remain to be qualified.

`SliderMotorScene.sx` starts uphill at −1 m/s on an inclined rail. T cycles
uphill, braking and downhill; F selects 30 or 6 N, with 6 N insufficient to
climb. D disables/enables the motor; R resets, Space pauses/resumes and
Escape closes the window.

[The position servo](SliderPosition3D.md) adds target travel through a damped spring.

The [slider friction brake](SliderFriction3D.md) slows travel without a motor using mutable maximum force.
