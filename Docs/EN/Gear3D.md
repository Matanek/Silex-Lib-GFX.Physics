# 3D gear

`World3D.create_gear_constraint` couples two bodies around their local axes
through θ₁ + ratio × θ₂ = 0. Positive ratios rotate in opposite directions;
negative ratios rotate in the same direction. Angles start at the creation
poses, in radians, with turn tracking.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var settings=Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0)
    var first=world.create_rigid_body(settings);var second=world.create_rigid_body(settings)
    var gear=world.create_gear_constraint(first,second,Physics.GearConstraint3DSettings() ..ratio=2.0)
    second.set_angular_velocity(Math.Vec3(0.0,0.0,1.0))
    world.step(1.0/60.0)
    assert(Math.abs(first.angular_velocity().z+0.4)<0.00001)
    assert(Math.abs(second.angular_velocity().z-0.2)<0.00001)
    assert(Math.abs(gear.first_reaction_torque().z+4.8)<0.0001)
    assert(Math.abs(gear.reaction_torque().z+9.6)<0.0001)
    assert(Math.abs(gear.phase_error())<0.00001 && Math.abs(gear.speed_error())<0.00001)
    gear.set_ratio(-1.0);world.step(1.0/60.0)
    assert(Math.abs(first.angular_velocity().z-second.angular_velocity().z)<0.00001)
    world.destroy_gear_constraint(gear);assert(!gear.is_valid())
    print("gear recipe: ok")
}
```

## Ratio, axes and reactions

`GearConstraint3DSettings` contains shape-local axes (Z by default), a signed
nonzero `ratio` (default 1) and `is_enabled`. Finite nonzero axes are normalized;
both the ratio and its square must be finite and nonzero in the numeric format.

The transmission holds neither positions nor axis inclination. Add hinges to
retain mechanical axles. Phase tracking assumes rotations around the declared
axes; freely tilting spatial chains are outside the witnesses. The ratio
relates angular speeds; the API does not impose a radius or integral tooth
count. There are no tooth contacts, motor, friction or spring in this family.

`phase_error()` measures θ₁ + ratio × θ₂ in radians; `speed_error()` measures
ω₁·axis₁ + ratio × ω₂·axis₂ in rad/s. External poses use the shortest angular
change and cannot communicate multiple turns between calls. During a step,
integrated angular velocity disambiguates turns, including more than π radians
per step. Phase correction is gradual and adds no kinetic energy.

`first_reaction_torque()` returns the first body's torque; `reaction_torque()`
returns the second body's torque, in world N·m. They are axis₁ × λ/dt and
axis₂ × ratio × λ/dt: total power vanishes when the speed equation holds.
Reactions come from the latest positive step; a zero step preserves them.

## Mutation and lifetime

`set_ratio` and `set_axes` take current poses as a new zero phase, clear
reactions and wake the bodies. `set_enabled` preserves phase: turns during
suspension remain observed and reactivation gradually recovers the error.
Disabling a body also suspends resolution. Getters expose the bodies, axes,
ratio, enabled state and validity; `World3D.gear_constraint_count` counts live
attachments.

Creation requires two distinct bodies of the same world, including a dynamic
body. A fixed or kinematic body can prescribe the dynamic body's rotation.
Destroying a body or world invalidates the handle; recycled slots never revive
old handles. Stale reads/mutations fail explicitly, except `is_valid()`.

## Qualification and reference boundary

Consumers cover positive/negative/fractional ratios, unequal inertias,
dissipative projection, power, phase, mutations, sleep, lifetime and hinged
motor transmission. Pinned Jolt witnesses compare unit ratios, distinct frames
and loads in Debug/Release. Its nonunit response omits the second torque's ratio;
ratio −1 injects energy. The harness preserves this reference divergence.
Affected ratios use independent mechanical equations without claiming parity
with the faulty response. General spatial chains and exact impact-step phase
remain outside these witnesses.
