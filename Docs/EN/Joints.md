# Joints, motors, and springs

`World2D` owns eight typed joint families matching the pinned Box2D 3.1.1
vocabulary: distance, filter, motor, mouse, prismatic, revolute, weld, and
wheel. Each creation function returns a handle named after its gameplay
intention; no common public constraint base, solver row, color, slot, or
generation is exposed.

Creation settings use world-space anchors, axes, and mouse targets. `World2D`
converts them to body-local solver data when the joint is created. The
`MotorJoint2DSettings.linear_offset` is the exception: it is deliberately an
offset in the first body's local frame, paired with an angular offset between
the two bodies.

```silex
var hinge = world.create_revolute_joint(
    chassis,
    arm,
    Physics.RevoluteJoint2DSettings()
        ..anchor = Math.Vec2(0.0, 1.0)
        ..lower_angle = -0.5
        ..upper_angle = 0.5
        ..motor_speed = 2.0
        ..maximum_motor_torque = 40.0
        ..limit_enabled = true
        ..motor_enabled = true
)
```

Typed handles expose the connected bodies and the retained local frames.
Every family then owns its applicable runtime properties: length, limits,
spring, motor, target, offsets, maxima, hertz, and damping. Mutators validate
their values, clear impulses made incompatible by the change, and wake the
connected island. Like every world mutation, they fail while `step` is active.

```silex
hinge.set_limits(true, -0.75, 0.75)
hinge.set_spring(true, 4.0, 0.7)
hinge.set_motor(3.0, 60.0)
```

The families express these distinct intentions:

- `DistanceJoint2D` retains an anchor distance and can add a length range, a
  spring, and a linear motor.
- `FilterJoint2D` only prevents collision between two connected bodies.
- `MotorJoint2D` drives a relative linear and angular offset with bounded force
  and torque.
- `MouseJoint2D` pulls one retained body point toward a mutable world target.
- `PrismaticJoint2D` permits translation on one axis and supports translation
  limits, a spring target, and a linear motor.
- `RevoluteJoint2D` shares one world anchor and supports angular limits, an
  angular spring target, and a rotary motor.
- `WeldJoint2D` retains the relative anchor and angle, optionally with distinct
  linear and angular spring tuning.
- `WheelJoint2D` combines one suspension axis with translation limits, a
  spring, and a rotary motor.

Connected collision is disabled by default. Set `collide_connected` when the
corresponding settings type exposes it and the two shapes should still collide.
The filter joint always disables connected collision and contributes no solver
impulse. Runtime `set_collide_connected` changes the same policy for every
other two-body family.

Distance and prismatic handles report current translation, speed where
relevant, constraint force, and motor force. Revolute and wheel handles
report angle or translation, constraint force and torque, and motor
torque. Mouse, motor, and weld handles expose their pertinent reactions.
These reactions describe the most recently completed `step`; they are zero
before a positive-duration step. Mouse targets and supported motor speeds can
be changed through their typed handles, which wakes the connected bodies.
`separation()` reports the current anchor separation without exposing solver
rows or accumulated impulses.

`world.write_joints(buffer)` enumerates all joints in stable creation order;
the `world.write_joints(body, buffer)` overload retains only joints attached to
that body. The caller-owned array contains the tagged `Joint2D` sum. Matching
its distance, filter, motor, mouse, prismatic, revolute, weld, or wheel case
recovers the corresponding specialized handle.

Joint handles follow the same ownership rule as body handles. Calling
`world.destroy_joint(joint)` invalidates every copy of that handle. Destroying
either attached body also destroys and invalidates the joint. A stale handle
fails explicitly when used, while `is_valid()` provides a non-failing lifetime
check.

All active joints enter the same deterministic twelve-color Soft Step graph as
contacts. A joint color is assigned only after contact colors have claimed
their body masks, so no worker in one color can mutate a body used by another
contact or joint in that color. The overflow color remains ordered and scalar;
large conflict-free colors use the same 4,096-entry dispatch threshold and the
same kernels for one or several workers. Joint-connected dynamic bodies also
share sleep-island lifetime.

[`Joints.sx`](../../Tests/Consumer/Tests/Joints.sx) and
[`JointRuntimeConfiguration.sx`](../../Tests/Consumer/Tests/JointRuntimeConfiguration.sx)
are the public executable proofs. They cover every family, runtime properties,
enumeration, reactions, collision suppression and handle invalidation;
internal tests add deterministic worker-count equivalence and a 4,096-joint
parallel color.

## Common constraint tuning and springs

Distance, prismatic, revolute, weld, and wheel expose `constraint_hertz`
(default 60 Hz), `constraint_damping_ratio` (default 2), and
`set_constraint_tuning(hertz, damping_ratio)`. Common tuning is independent
of springs and motors. Its effective frequency is capped at one quarter of
the inverse substep duration; getters retain the configured value. A zero
frequency disables position correction while relaxation retains the velocity
constraint.

| Joint | Constraints using common tuning |
|---|---|
| Distance | Rigid length; length limits while the spring is enabled |
| Prismatic | Perpendicular translation and relative angle; translation limits |
| Revolute | Coincident anchors; angular limits |
| Weld | Linear constraint when `linear_hertz` is zero and angular constraint when `angular_hertz` is zero |
| Wheel | Perpendicular translation; translation limits |

```silex
var tether = world.create_distance_joint(chassis, arm,
    Physics.DistanceJoint2DSettings()
        ..first_anchor = Math.Vec2()
        ..second_anchor = Math.Vec2(2.0, 0.0)
        ..length = 1.0
        ..constraint_hertz = 5.0
        ..constraint_damping_ratio = 2.0)
tether.set_constraint_tuning(8.0, 3.0)
assert(tether.constraint_hertz() == 8.0)
assert(tether.constraint_damping_ratio() == 3.0)
```

Frequency and damping must be finite and nonnegative at creation and mutation.
Mutation wakes the bodies, retains accumulated impulses, and preserves spring,
limit, and motor settings. A destroyed handle or mutation during `step` fails
explicitly.

Springs retain their own frequency and damping. They also act during
relaxation, without the common tuning frequency cap. Their impulses remain
independent from limit and motor impulses. For distance, enable the spring to
combine the length range and motor. With the spring disabled, or enabled
limits of equal length, the joint retains `length`: the motor and range do
not replace that rigid length. For weld, a positive family frequency replaces
common tuning only for its linear or angular component.

## Reactions and differential evidence

Reported forces and torques use the substep duration. They follow the pinned
Box2D 3.1.1 conventions: prismatic force and revolute torque exclude their
spring impulse; distance, wheel, and weld reactions include it. Wheel force
uses the axis retained at the beginning of the most recent step, even when
the body rotated during that step.

The [distance tests](../../Tests/Consumer/Tests/DistanceConstraintTuning.sx)
and [other four family tests](../../Tests/Consumer/Tests/JointConstraintTuning.sx)
cover creation, getters, mutation, independent settings, and wake-up.
The [tuning](../../Benchmarks/JointConstraintTuningOracle2D.sx) and
[combination](../../Benchmarks/JointCombinationsOracle2D.sx) oracles compare
2,688 and 3,840 samples respectively: 1/2/4/8 substeps, central or offset
anchors, a fixed body or two moving bodies, and an oblique axis. Fixed
tolerances cover positions, angles, velocities, forces, and torques; these
corpora do not guarantee every possible physics scene.
