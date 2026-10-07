# Dampen slider stops

`limit_spring` lets a stop compress under load before returning the carriage.
`SliderLimitSpring3D(stiffness, damping)` specifies stiffness in N/m and
damping in N·s/m; `null` retains rigid stops.

This motor compresses the positive stop by 0.25 m and the negative stop by
0.0625 m because its permitted effort differs in each direction.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail,carriage,Physics.SliderConstraint3DSettings()
        ..minimum_position = -0.3 ..maximum_position = 0.3
        ..limit_spring = Physics.SliderLimitSpring3D(stiffness:8.0,damping:8.0)
        ..motor = Physics.SliderMotor3D(speed:1.0,minimum_force:-0.5,maximum_force:2.0))
    var step = 0;while step<1200 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()-0.55)<0.001 && Math.abs(joint.limit_force()+2.0)<0.001)
    joint.set_motor(Physics.SliderMotor3D(-1.0,-0.5,2.0))
    step = 0;while step<1440 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()+0.3625)<0.001 && Math.abs(joint.limit_force()-0.5)<0.001)
    let spring = joint.limit_spring()!
    assert(spring.stiffness==8.0 && spring.damping==8.0)
    joint.set_limit_spring(null)
    step = 0;while step<120 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()+0.3)<0.0001)
}
```

A positive force of 2 N with 8 N/m stiffness produces 0.25 m deformation:
the carriage settles at 0.55 m despite the nominal 0.3 m bound. On reversal,
0.5 N negative effort produces 0.0625 m deformation. Removing the spring
restores rigid response at the same bounds. The [signed motor](SliderForceBounds3D.md)
and stop retain separate observations: `motor_force()` and `limit_force()`.

A soft stop becomes active when travel reaches or exceeds its bound at the
start of the step. Crossing from the interior activates it on the next step;
pose is not projected onto a soft bound. The lower stop pushes positively,
the upper negatively, on body two. A stop never pulls a carriage returning
into its interval. Equal bounds form a bilateral spring; without damping,
it oscillates around that travel. With no bounds, the spring leaves travel free.

Stiffness must be positive and finite, damping nonnegative and finite.
The setting is immutable; `limit_spring()` returns an optional value snapshot.
`set_limit_spring(...)` replaces the setting, clears reactions and wakes bodies.
`set_limit_spring(null)` restores rigid stops. A zero step retains observations.
Suspension, destruction, frames and bound mutations follow [slider](Slider3D.md)
rules. [Motors](SliderMotor3D.md) or [friction](SliderFriction3D.md) may act with
soft stops; the spring does not replace their budgets. [Servo](SliderPosition3D.md)
targets still project into the nominal interval, even with a soft stop.

Tests check 60/120 Hz recurrences, oscillation and energy, overshoot in both
directions, unequal masses, 3D COM/anchors, load, mutations, sleep and real
contact. Eight Debug/Release Jolt trajectories also qualify against independent
mechanics. Hard impact, rotating-rail transients and general spatial chains
remain outside this qualification. Combined slider commands remain to be qualified.

`SliderSoftLimitsScene.sx` compares a damped gold carriage with an undamped
blue one: gold settles, blue oscillates. T kicks in alternating directions,
R resets, Space pauses/resumes and Escape quits.
