# 3D pulley

`World3D.create_pulley_constraint` connects two bodies to two fixed world
points. Its weighted length is L₁ + ratio × L₂. By default the cable may go
slack but cannot exceed its creation length. A positive ratio models a block
and tackle: the second branch carries ratio times the first branch's tension.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D()
    var first=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..transform=Physics.Transform3D(Math.Vec3(-1.0,0.0,0.0))
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var second=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..transform=Physics.Transform3D(Math.Vec3(1.0,0.0,0.0))
        ..mass_properties=Physics.MassProperties3D(4.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var joint=world.create_pulley_constraint(first,second,
        Physics.PulleyConstraint3DSettings(Math.Vec3(-1.0,2.0,0.0),Math.Vec3(1.0,2.0,0.0)) ..ratio=2.0)
    var i=0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.length()-6.0)<0.001 && Math.abs(joint.speed())<0.001)
    assert(Math.abs(joint.first_reaction_force().y-19.62)<0.001)
    assert(Math.abs(joint.reaction_force().y-39.24)<0.001)
    joint.set_limits(0.0,8.0);world.step(1.0/60.0)
    assert(joint.reaction_force().length()==0.0)
    joint.set_ratio(1.0);assert(joint.maximum_length()==8.0)
    world.destroy_pulley_constraint(joint);assert(!joint.is_valid())
    print("pulley recipe: ok")
}
```

## Anchors and limits

`PulleyConstraint3DSettings(first_world_anchor, second_world_anchor)` requires
the fixed points. `first_local_anchor` and `second_local_anchor` are shape-local
body anchors, at the origin by default. Fixed points follow neither body.
`ratio` is positive and defaults to 1; its square must remain finite and
nonzero in the numeric format.

`minimum_length` defaults to 0; `maximum_length=null` captures the initial
weighted length. Limits must be finite, ordered and nonnegative. Equal limits
hold a rigid length. A positive minimum can push when branches become too
short; keep the minimum at 0 for a cable that only pulls. Cable geometry must
remain finite and representable.

`first_length()` and `second_length()` measure branch lengths in meters;
`length()` returns the weighted sum and `speed()` its rate in m/s, using
anchor velocities. A zero-length branch retains its last known direction,
initially and after a mutation −Y. This is a singularity convention, not a direction inferred from
a zero segment. This family adds no motor, friction or spring.

## Reactions, mutation and lifetime

`first_reaction_force()` and `reaction_force()` return the first and second
body's world forces in N. `first_reaction_torque()` and `reaction_torque()`
return their anchor moments in N·m, including the force lever rather than an
extra free couple. They record impulses actually applied during the latest
positive step; a zero step preserves them. The velocity Jacobian is prepared
before pose integration with that step's lever arms and inertia responses.
Length correction adds no kinetic energy.

`set_local_anchors`, `set_world_anchors` and `set_ratio` retain configured
numeric limits. `set_limits` replaces both limits; use
`set_limits(0.0, joint.length())` to recapture a slack cable. All mutations and
`set_enabled` clear reactions and wake the bodies. Disabling a body or the
constraint suspends resolution. Anchor/limit/ratio/state getters, `first_body`,
`second_body` and `is_valid` provide observations;
`World3D.pulley_constraint_count` counts live constraints.

Creation requires two distinct bodies from the same world, including a dynamic
body. A fixed endpoint can retain the other load. Destroying a body or world
invalidates handles; slot reuse never revives old handles. Stale operations
fail explicitly except `is_valid()`; `World3D.destroy_pulley_constraint`
explicitly removes a pulley.

## Qualification

Consumers and Jolt Debug/Release cover tension, slack, tackle ratios, unequal
masses, balanced loads or Atwood motion, length mutation, offset anchors and
a rotated frame. Independent velocity projections, effort and position
recurrences accompany the comparisons. Tests add a lower limit, energy,
singularity handling, sleep, lifetime and real floor contact. Analytic Atwood
energy propagates velocity tolerance; pairwise Jolt energy retains its 0.05 J
bound. General spatial chains and exact impact-step phase remain outside
these witnesses.

[Mixed assemblies](TerrainConstraintQualification3D.md) add two SixDOF guides
and ground contact with explicit position budgets.
