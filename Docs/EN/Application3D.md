# Integrate World3D with Application and Scene3D

`Plugins.Physics3D` installs a `Resources.World3D` in the current Application
context. It adds ECS and the clock, but no window, renderer, or
`Plugins.Scene3D`. A headless consumer can therefore use the same components
as the [Scene3D demonstration](../../../../Silex-Examples/Sources/Physics3D/RigidScene.sx).

```silex
use GFX.Application
use GFX.Components
use GFX.ECS
use GFX.Physics
use GFX.Plugins
use GFX.Resources
use STD.Math

var application = Application()
    ..add_plugin(Plugins.Physics3D(Plugins.Physics3D.Settings()
        ..world = (Physics.World3DSettings() ..gravity = Math.Vec3())
        ..fixed_delta = 1.0 / 60.0
        ..maximum_catch_up_steps = 4
    ))

func create_body(world:&Resources.World) {
    world.spawn(ECS.EntityRecipe()
        ..with(Components.Transform3D(position:Math.Vec3(0.0, 3.0, 0.0)))
        ..with(Components.PhysicsBody3D(Physics.RigidBody3DSettings()
            ..shape = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(0.8)))))
    )
}
```

An entity receives a body when it has both `Components.Transform3D` and
`Components.PhysicsBody3D`. The ECS pose is global and measured in metres;
`Node3D` already composes parent poses before publishing its ECS component.
Global scale must be one: size the shape and mesh explicitly. A non-unit
scale, invalid physical position, or invalid rotation is rejected. The plugin
does not silently convert poses.
`Nodes.StaticBody3D` provides a fixed obstacle below a `Node3D` parent using
the same global composition.

At creation, the ECS pose initializes the body. Physics then owns the pose of
a dynamic body and publishes its position and rotation to
`Components.Transform3D` after each step. The ECS pose drives a fixed body or
becomes the kinematic target at the next fixed step. An external edit to a
dynamic ECS transform is replaced by the physical pose; use the handle from
`PhysicsBody3D.body()` and body commands to move it. The binding respects
entity lifetime and generation.

The plugin accumulates frame time and executes at most
`maximum_catch_up_steps` steps of duration `fixed_delta` per frame. Any
remainder waits for the next frame. While `Application.Simulation` is paused,
no step runs and paused time does not enter the accumulator. A disabled entity
retains its body but leaves collisions; reactivation restores its previous
enabled setting. Removing the entity or either component destroys the body,
even during a pause.

`Resources.Physics3DFrameEvents` collects contact begins and ends from all
steps in one frame, through `fixed_step_count()`, `contact_begin_count()`,
`contact_end_count()`, `contact_begin(index)`, and `contact_end(index)`. The
resource clears at every `post_update`, including paused frames. An end queued
by destruction becomes visible at the next positive step. `Contact3D`
snapshots follow the [3D world](World3D.md) lifetime rules.

A consumer plugin can register `Physics.Physics3DStep.before_step` and
`after_step` from its `build` method. Each `func(Application, float)` callback
runs once per actual step, after body binding and at a safe boundary with no
active ECS query. Physics2D and Physics3D have separate worlds, accumulators,
callbacks, and events within one Application. The scene reads physical poses
at `Schedule.render`, after physics `post_update`.

The headless proof is
[`Application3DIntegration.sx`](../../Tests/Consumer/Tests/Application3DIntegration.sx).
