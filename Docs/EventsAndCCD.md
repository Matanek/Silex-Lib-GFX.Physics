# CCD, sensors, and post-step events

`World2D` collects simulation feedback in deterministic buffers. It never
invokes gameplay callbacks from a worker. Read the enabled streams immediately
after `step` and before destroying a body named by an event.

## Enable only the streams a body needs

Event generation is opt-in at body creation:

```silex
let trigger = Physics.RigidBody2DSettings()
    ..body_type = Physics.BodyType2D.fixed
    ..shape = Physics.Shape2D.box(Physics.Box2D(Math.Vec2(2.0)))
    ..is_sensor = true
    ..enable_sensor_events = true

let projectile = Physics.RigidBody2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.1))
    ..is_bullet = true
    ..enable_move_events = true
    ..enable_contact_events = true
    ..enable_hit_events = true
```

`Collider2DSettings.is_sensor` disables physical response for that collider but
keeps its overlap filtering. The retained body-level fields configure the
implicit compatibility collider. `enable_sensor_events` belongs to the sensor;
an ordinary visitor does not need
to opt in. When two enabled sensors overlap, each receives its own event role.
Contact and hit events are enabled when either solid body requests that stream.

The flags are immutable body settings. This avoids mismatched begin/end pairs
caused by changing an event policy while a pair is already touching. Disabled
streams do not build payloads, and a world without bullets does not enter the
dynamic-target CCD path.

## Read completed-step buffers

```silex
var began:Physics.ContactBeginEvent2D[] = []
var ended:Physics.ContactEndEvent2D[] = []
var hits:Physics.ContactHitEvent2D[] = []
var sensor_began:Physics.SensorBeginEvent2D[] = []
var sensor_ended:Physics.SensorEndEvent2D[] = []
var moves:Physics.BodyMoveEvent2D[] = []

world.step(1.0 / 60.0)
world.write_contact_begin_events(began)
world.write_contact_end_events(ended)
world.write_contact_hit_events(hits)
world.write_sensor_begin_events(sensor_began)
world.write_sensor_end_events(sensor_ended)
world.write_body_move_events(moves)
```

Every `write_*_events` call clears and refills the caller's list. Begin contact
events contain the completed-step manifold. Hit events contain a world point,
a normal oriented from `first_body` to `second_body`, and the positive approach
speed. `World2D` defaults the hit threshold to `1 m/s`; pass
`hit_event_threshold` to the constructor or call
`set_hit_event_threshold` between steps.

Move events contain the completed transform. `fell_asleep` marks the one event
that completes an awake-to-sleep transition; a moved event without that flag
represents an awake body. Direct user mutations do not themselves create move
events.

Pair roles use stable creation identity and streams follow deterministic pair
traversal. The same scene therefore produces the same logical order with one
or several workers. A fast
bullet that enters and leaves a thin sensor inside one step produces both the
begin and end sensor events in that step, so the trigger crossing is not lost.

## Continuous motion

Fast ordinary bodies retain the inexpensive fixed-box boundary protection used
by the solver. `is_bullet` deliberately expands continuous collision work to
dynamic targets and all public convex geometry. Linear motion uses the common
shape-cast geometry; angular motion searches the swept poses and refines the
first overlap. The earliest solid hit clips the bullet and removes inward
motion. Sensors report the crossing without clipping or applying an impulse.

The CCD path preserves collision filters and filter-joint exclusions. It does
not turn every dynamic pair into a continuous pair: that cost is paid only by
bullets. Solver callbacks and general concurrent world mutation remain outside
the contract. `World2D` and its body and joint handles reject mutation while
`step` is active; post-step buffers are the supported place for gameplay to
react and then mutate the world.

The headless executable proof is
[`../Examples/World2D/Events.sx`](../Examples/World2D/Events.sx):

```text
silex run Packages/GFX.Physics/Examples/World2D/Events.sx
```
