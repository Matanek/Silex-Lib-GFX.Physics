# 3D rack and pinion

`World3D.create_rack_and_pinion_constraint(pinion, rack, settings)` couples
rotation and travel through θ = ratio × travel. The signed ratio is in
rad/m: a pitch radius R corresponds to |ratio| = 1/R. Its sign depends on
the selected axis and rotation directions.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var settings=Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0)
    var pinion=world.create_rigid_body(settings);var rack=world.create_rigid_body(settings)
    var joint=world.create_rack_and_pinion_constraint(pinion,rack,
        Physics.RackAndPinionConstraint3DSettings() ..ratio=2.0)
    rack.set_linear_velocity(Math.Vec3(1.0,0.0,0.0));world.step(1.0/60.0)
    assert(Math.abs(pinion.angular_velocity().z-10.0/7.0)<0.00001)
    assert(Math.abs(rack.linear_velocity().x-5.0/7.0)<0.00001)
    assert(Math.abs(joint.pinion_reaction_torque().z-120.0/7.0)<0.0001)
    assert(Math.abs(joint.reaction_force().x+240.0/7.0)<0.0001)
    assert(Math.abs(joint.pinion_angle()-2.0*joint.travel())<0.00001)
    joint.set_ratio(-1.0);assert(joint.travel()==0.0 && joint.pinion_angle()==0.0)
    world.step(1.0/60.0);assert(Math.abs(joint.speed_error())<0.00001)
    world.destroy_rack_and_pinion_constraint(joint);assert(!joint.is_valid())
    print("rack recipe: ok")
}
```

## Axes and mechanical use

`RackAndPinionConstraint3DSettings` contains `pinion_local_axis` (Z),
`rack_local_axis` (X), `ratio` (1 rad/m) and `is_enabled`. Axes are shape-local
and normalized. They must be finite and nonzero; both the ratio and its square
must be finite and nonzero in the numeric format.

Retain the pinion with a hinge and the rack with a slider: this coupling
only provides transmission. It holds neither centers nor other rotations.
The rack must retain its orientation and the pinion rotate around its axis.
Freely tilting axes are outside the witnesses. No tooth contacts, extra motor,
friction or spring are added; drive the hinge or slider to power the mechanism.

`travel()` measures the rack center-of-mass displacement from its reference
position, projected on its axis, in meters. `pinion_angle()` tracks turns from
the reference orientation in radians. `phase_error()` is θ − ratio × travel
in radians; `speed_error()` is ωp·axisp − ratio × vr·axisr in rad/s. Tracking
disambiguates turns within a step, including more than π radians; external
poses use their shortest angular change. Phase correction is gradual and
adds no kinetic energy.

## Reactions and mutation

`pinion_reaction_torque()` is the pinion torque in N·m; `reaction_force()` is
the rack force in N, both in world coordinates. Their impulses are axisp × λ
and −ratio × axisr × λ. Total power vanishes when the speed equation holds.
Reactions come from the latest positive step; a zero step preserves them.

`set_axes` and `set_ratio` use current poses as the new reference, clear
reactions and wake the bodies. `set_enabled` preserves phase during suspension;
reactivation gradually recovers the error. Disabling a body also suspends
resolution. `pinion_body`, `rack_body`, axes/ratio/state getters and `is_valid`
provide observations; `World3D.rack_and_pinion_constraint_count` counts live
transmissions.

Creation requires two distinct bodies from the same world, including a dynamic
body. A fixed or kinematic endpoint can prescribe the other body's speed.
Destroying a body or world invalidates the handle; slot reuse never revives
old handles. Stale operations fail explicitly except `is_valid()`;
`World3D.destroy_rack_and_pinion_constraint` explicitly removes a transmission.

## Qualification

Consumers and pinned Jolt Debug/Release cover signed/fractional ratios,
unequal masses, a rotated frame, sustained load and reactions. Independent
projection and travel equations accompany the comparisons. Tests add turns,
phase, mutations, suspension, sleep, lifetime and hinge/slider transmission,
including a slider stop or real obstacle contact. General spatial chains and
exact impact-step phase remain outside these witnesses. The gear oracle
defect does not affect this family: pinned Jolt applies the ratio to its
linear impulse here.
