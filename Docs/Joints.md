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
impulse.

Distance and prismatic handles report current translation, speed where
relevant, total constraint force, and motor force. Revolute and wheel handles
report angle or translation, total constraint force and torque, and motor
torque. Mouse, motor, and weld handles expose their pertinent total reactions.
These reactions describe the most recently completed `step`; they are zero
before a positive-duration step. Mouse targets and supported motor speeds can
be changed through their typed handles, which wakes the connected bodies.

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

[`../Tests/Consumer/Tests/Joints.sx`](../Tests/Consumer/Tests/Joints.sx) is the
public executable proof. It covers every family, limits, motors, springs,
reactions, collision suppression and handle invalidation; internal tests add
deterministic worker-count equivalence and a 4,096-joint parallel color.
