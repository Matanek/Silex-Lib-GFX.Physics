# Six degrees of freedom

`World3D.create_six_dof_constraint` configures X/Y/Z translations and rotations
independently. All degrees are free by default.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var support=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type=Physics.BodyType3D.fixed ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var body=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep=false ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    let locked=Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.locked
    let travel=Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.bounded(-0.3,0.3)
        ..motor=Physics.LinearMotor3D.position(0.2,100.0,20.0,8.0)
    var joint=world.create_six_dof_constraint(support,body,Physics.SixDOFConstraint3DSettings()
        ..translation_x=travel ..translation_y=locked ..translation_z=locked
        ..swing_limits=Physics.SwingLimits3D.cone(Math.Vec2())
        ..minimum_twist=-0.4 ..maximum_twist=0.4
        ..rotation_x_motor=Physics.AngularMotor3D.position(0.1,10.0,2.0,1.0))
    var i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.translation().x-0.2)<0.002 && Math.abs(joint.twist_angle()-0.1)<0.002)
    joint.set_rotation_x_motor(null)
    joint.set_translation_x(Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.bounded(-0.3,0.3)
        ..motor=Physics.LinearMotor3D.position(-0.15,100.0,20.0,8.0))
    assert(joint.motor_force().length()==0.0 && joint.motor_torque().length()==0.0)
    i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.translation().x+0.15)<0.002)
    world.destroy_six_dof_constraint(joint);assert(!joint.is_valid())
    print("six DOF recipe: ok")
}
```

## Translations and frames

`first_local_frame` and `second_local_frame` origins and rotations are local
to body shape frames, as in swing/twist. Translations follow the first frame's
axes. `translation()` is the second anchor relative to the first in that frame,
in meters. `translation_speed()` is its derivative in m/s, including rotation
of the first frame. `anchor_error()` is that displacement in world space;
nonzero values are admissible for free degrees or ranges away from zero.

`translation_x`, `translation_y` and `translation_z` each contain a
`LinearAxis3DSettings`. `LinearLimit3D.free` releases motion, `locked` fixes
the zero coordinate, and `bounded(minimum, maximum)` defines finite strictly
ordered positions in meters. Move a frame origin to lock another reference
coordinate.

`limit_spring=LinearLimitSpring3D(stiffness, damping)` makes a locked or bounded
limit elastic: positive stiffness in N/m and nonnegative damping in N·s/m.
Elastic stops allow compression under load and do not directly correct
position. Their effort is independent of motor capacity; equilibrium
compression under constant load F is F/k. Springs on free degrees are rejected.

## Rotations and drives

`minimum_twist` and `maximum_twist` bound X twist in radians. `swing_limits`
provides an elliptical cone or pyramid for Y/Z. See [swing/twist geometry](SwingTwist3D.md)
for angle conventions, the 180° singularity and frames. Pyramids may exclude
zero; equal bounds lock an angle, including a nonzero angle.

Each translation accepts a `LinearMotor3D`: speed in m/s, force bounds in N,
position in meters, stiffness in N/m and damping in N·s/m.
`rotation_x_motor`, `rotation_y_motor` and `rotation_z_motor` each accept an
`AngularMotor3D`: speed in rad/s, torque in N·m, target in radians, stiffness
in N·m/rad and damping in N·m·s/rad. Angular directions are carried by the
second frame. Y/Z targets are swing coordinates; commanded velocities are
not their coordinate derivatives during combined rotations.

Constructors provide velocity and symmetric capacity, or signed
`minimum_force/torque` and `maximum_force/torque` bounds. `position` and
`position_and_velocity` factories add a target and damped spring. Targets
are projected onto limits. All three drives have independent budgets and
parameters; absent position drives preserve their current part in the
composed angular target.

`maximum_friction_force` brakes an unpowered translation.
`maximum_rotation_friction_torque` provides X/Y/Z capacities for unpowered
rotations. Capacities are finite and nonnegative, defaulting to zero.
A present zero-capacity motor replaces friction; `null` restores it.

## Reactions and mutation

`reaction_force()` and `reaction_torque()` are the world-space force in N and
free torque in N·m on the second body; torque excludes the moment of anchor
forces. `motor_force`, `friction_force` and `limit_force` give scalar X/Y/Z
linear-axis efforts, while `motor_torque` and `friction_torque` give angular
drive efforts. They describe the last positive step; a zero step preserves
them. Use world-space reactions for a resulting global direction.

`set_translation_x/y/z` replaces the entire axis configuration.
`set_rotation_x/y/z_motor`, `set_maximum_rotation_friction_torque`,
`set_swing_limits`, `set_twist_limits`, `set_frames`, `set_anchors` and
`set_enabled` clear reactions and wake linked bodies. Creation requires
distinct bodies in the same world with at least one dynamic body. Disabling
a body or the joint suspends solving. Explicit removal or destruction of
either body or the world invalidates the handle; only `is_valid()` remains
usable on a stale handle.

## Qualification

Headless consumers cover free/locked/bounded degrees, independent and
simultaneous drives, friction, loaded soft stops, rotated frames, unequal
masses, an offset anchor at rest, contacts and lifetime. Linear and angular
servos are checked against independent 60/120 Hz recurrences; a pinned Jolt
Debug/Release witness covers sixteen reduced cases. General spatial chains,
loaded offset servos and exact impact-step reaction parity remain to be qualified.
