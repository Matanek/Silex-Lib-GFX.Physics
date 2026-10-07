# 3D slider axial friction

`SliderConstraint3DSettings.maximum_friction_force` passively brakes a
carriage's relative travel. Symmetric capacity is in N, finite and
nonnegative; zero, the default, leaves travel free. Friction can stop
motion and hold an axial load below capacity without setting a target position.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    carriage.set_linear_velocity(Math.Vec3(1.0, 0.0, 0.0))
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings() ..maximum_friction_force = 2.0)
    var step = 0
    while step < 240 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001)
    joint.set_maximum_friction_force(0.0)
    carriage.set_linear_velocity(Math.Vec3(-0.5, 0.0, 0.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() + 0.5) < 0.0001 && joint.friction_force() == 0.0)
    joint.set_maximum_friction_force(1.0)
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001 && joint.maximum_friction_force() == 1.0)
}
```

`maximum_friction_force()` reads capacity and `set_maximum_friction_force(force)`
replaces it, clears reactions and wakes both bodies. Creation settings are
copied. `friction_force()` reports signed force in N applied to the second
body during the last positive step: it opposes relative speed along X of the
first frame or holds a load at rest. The bound is shared across all passes
of the step; stopping does not reverse velocity.

An installed [velocity motor](SliderMotor3D.md) or [position servo](SliderPosition3D.md)
takes precedence, including at zero capacity. `set_motor(null)` restores
friction with its retained capacity. Motor and friction efforts are observed
separately; `reaction_force()` also includes restraints and stops.
`reaction_torque()` can compensate the moment at an offset anchor.

This axial brake force is independent of contact material friction. Stops,
contacts and [slider](Slider3D.md) lifetime rules remain active. A zero step
retains observations; changing frames, limits or activation clears them.
Suspending a body or constraint clears efforts at the next positive step.
Friction alone does not artificially keep a resting assembly awake.

Tests cover 60/120 Hz, both signs, stopping, load, reduced mass, offset 3D
COM/anchors, mutations, motor precedence, sleep, suspension, stops and real
contacts. The Debug/Release Jolt oracle checks eight 60 Hz trajectories:
signed braking, offset anchor, two masses, mutations, motor modes, zero
capacity and load holding/release. Rotating transient, impact and general
spatial-chain parity remain unestablished; further slider extensions remain
to be qualified.

`SliderFrictionScene.sx` shows a gold carriage on an inclined rail. F enables
or removes the brake; T launches alternately uphill and downhill. R restarts,
Space pauses/resumes and Escape quits.
