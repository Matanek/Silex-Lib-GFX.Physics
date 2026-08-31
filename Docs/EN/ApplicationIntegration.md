# Application, ECS, and Scene2D integration

`Plugins.Physics2D` installs an independent `Resources.World2D` in the current
Application context. The plugin adds only ECS and the application clock: it
requires no window, renderer, camera, or statistics panel.

```silex
use GFX.Application
use GFX.Components
use GFX.ECS
use GFX.Physics
use GFX.Plugins
use GFX.Resources
use STD.Math

var application = Application()
    ..add_plugin(Plugins.Physics2D(Plugins.Physics2D.Settings()
        ..world = (Physics.World2DSettings() ..gravity = Math.Vec2(0.0, 9.81))
        ..fixed_delta = 1.0 / 60.0
        ..maximum_catch_up_steps = 4
        ..scene_units_per_meter = 100.0
        ..execution = Physics.Physics2DExecutionMode.workers(4)
    ))
```

An entity is bound to the world while it has both `Components.Transform2D` and
`Components.PhysicsBody2D`:

```silex
world.spawn(ECS.EntityRecipe()
    ..with(Components.Transform2D(position:Math.Vec2(0.0, 4.0)))
    ..with(Components.PhysicsBody2D(Physics.RigidBody2DSettings()
        ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.25))
        ..enable_move_events = true
    ))
)
```

`scene_units_per_meter` converts Scene2D positions to the physics world's meter
contract. The ECS transform selects the initial pose. Physics then owns dynamic
poses and publishes them after the frame's completed steps. ECS transforms are
copied to fixed bodies before each step. A kinematic ECS transform becomes a
target for the next fixed step.

The optional `PhysicsBody2D.colliders` array describes the complete compound
collider set. A non-empty array disables the implicit collider from
`RigidBody2DSettings`. Creation settings are immutable; replacing the component
explicitly recreates its body.

## Cadence and events

The accumulator retains time beyond `maximum_catch_up_steps` and processes it
on later frames instead of dropping fixed steps. Every completed step appends,
in order, to `Resources.Physics2DFrameEvents`. This resource publishes the step
count, body movements, contact begin/end/hit events, and sensor
begin/end/overlap events. It is cleared at the beginning of the next physics
update.

The `synchronous` mode uses one worker. `workers(count)` creates the world's
persistent pool; both modes preserve the same logical sequence.

ECS commands flush during `post_update`. A spawned entity is therefore bound on
the following update. Destroying the entity, removing either component, or
replacing the physics component invalidates its handle exactly once during that
reconciliation. No `ECS.Query` escapes the system that receives it.

The isolated proof is
[`ApplicationIntegration.sx`](../../Tests/Consumer/Tests/ApplicationIntegration.sx).
