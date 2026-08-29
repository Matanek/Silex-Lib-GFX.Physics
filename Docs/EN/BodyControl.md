# Mass, forces, and body control

`RigidBody2D` gathers the intentions needed to drive a body without duplicating
physics integration in application code. Every mutation requires an unlocked
world, so an attempted call during `World2D.step` fails explicitly.

## Composed mass

Mass, local center of mass, and rotational inertia derive from every living
collider, its geometry, and its density. Adding, removing, or changing a
collider recomputes these properties. The world center includes the body's
current transform.

```silex
let properties = body.mass_properties()
print(properties.mass)
print(body.local_center_of_mass())
print(body.world_center_of_mass())
print(body.rotational_inertia())
```

An explicit override remains available. It stays active through collider
mutations until it is removed:

```silex
body.set_mass_properties(Physics.MassProperties2D(
    mass:12.0,
    rotational_inertia:8.0,
    local_center:Math.Vec2(0.25, 0.0)
))

body.reset_mass_from_colliders()
```

At creation, `RigidBody2DSettings.mass = 0.0` means “derive from colliders.” A
strictly positive value retains the historical scalar-override shortcut. A
dynamic body without positive mass cannot receive a force or impulse.

## Forces and impulses

A force or torque accumulates until the next `step`, then is cleared. An
impulse changes velocity immediately. Point variants take a world point and
also produce angular motion around the center of mass.

```silex
body.apply_force_to_center(Math.Vec2(20.0, 0.0))
body.apply_force(Math.Vec2(0.0, 5.0), world_point)
body.apply_torque(2.0)

body.apply_linear_impulse_to_center(Math.Vec2(1.0, 0.0))
body.apply_linear_impulse(Math.Vec2(0.0, 1.0), world_point)
body.apply_angular_impulse(0.5)
```

Every action accepts `wake:bool = true`. With `wake = false`, an action on a
sleeping body is ignored. Physical actions require a dynamic, enabled, valid
body with positive mass; torque and angular impulse additionally require free
rotation.

## Frames and point velocity

The body converts points and vectors directly between its frames. Points
include translation, while vectors do not:

```silex
let world_point = body.world_point(local_point)
let local_point_again = body.local_point(world_point)
let world_direction = body.world_vector(local_direction)
let local_direction_again = body.local_vector(world_direction)

let velocity_here = body.world_point_velocity(world_point)
let velocity_there = body.local_point_velocity(local_point)
```

The public linear velocity belongs to the center of mass. Point velocity adds
the contribution from angular velocity.

## Runtime control

The following settings exist at creation and remain mutable outside a step:
type, gravity scale, damping, sleep threshold and permission, fixed rotation,
bullet state, activation, and debug label. Matching getters expose the current
state.

```silex
body.set_body_type(Physics.BodyType2D.dynamic)
body.set_gravity_scale(0.5)
body.set_linear_damping(0.2)
body.set_angular_damping(0.4)
body.set_sleep_threshold(0.03)
body.set_sleep_enabled(false)
body.set_fixed_rotation(true)
body.set_bullet(true)
body.set_debug_label("player")
```

`set_fixed_rotation(true)` clears angular velocity and removes inertia from
the response. `set_enabled(false)` preserves the handle and its transform but
removes the body from contacts, events, queries, and islands on the next step;
re-enabling rebuilds its participation.

An enabled kinematic body can target a transform over a duration:

```silex
body.set_target_transform(
    Physics.Transform2D(position:target_position, rotation:target_rotation),
    0.5
)
```

This selects the linear and angular velocities that reach the target, using
the shortest rotational path. The application keeps calling `step` over the
specified duration.

The consumer proofs live in
[`Tests/Consumer/Tests/BodyControl.sx`](../../Tests/Consumer/Tests/BodyControl.sx),
with failure cases in
[`Tests/Consumer/check-body-control.sh`](../../Tests/Consumer/check-body-control.sh).
The Box2D differential witness is documented in
[`Benchmarks/Oracle2D/README.md`](../../Benchmarks/Oracle2D/README.md).
