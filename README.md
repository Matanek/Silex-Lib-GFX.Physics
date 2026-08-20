# GFX.Physics

`GFX.Physics` is the optional physics extension for GFX. It begins with a
small, headless 2D simulation API and grows through executable examples.

```text
silex install path/to/GFX.Physics
```

```silex
use GFX.Physics
use STD.Math

var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..position = Math.Vec2(0.0, 10.0)
    ..rotation = 0.15
    ..friction = 0.75
)

world.step(1.0 / 60.0)
print(body.position())
```

When both packages are active, the same owned declarations are also available
through GFX's umbrella catalogs:

```silex
use GFX.Components
use GFX.Resources

let world = Resources.World2D()
let body:Components.RigidBody2D = world.create_rigid_body()
```

These are reexports contributed by `GFX.Physics`; their implementation and
ownership remain in this package.

The current 2D slice integrates linear and angular motion with a semi-implicit
Euler step. Oriented boxes can be fixed or dynamic and collide through a small
iterative impulse solver with rectangle inertia, restitution, and Coulomb
friction. A balanced dynamic AABB tree with fat proxies reduces the pairs sent
to the collision solver, retains broad-phase candidates across steps, and
filters them with tight bounds before solving. Parallel faces use a two-point
contact manifold with coupled normal impulses, keeping resting stacks stable
under friction. Contact impulses persist across steps and warm-start the next
solve. Resting contact islands sleep atomically after their residual surface
motion remains below the stability thresholds. A meaningful impact or
penetration wakes the affected sleeping support again.

Large moving worlds can opt into the persistent STD worker pool:

```silex
world.enable_parallelism(4)
```

The dynamic tree then discovers pairs through a lock-free two-pass job: it
counts each moved proxy's pairs, reserves one contiguous output, and fills
disjoint ranges in parallel. `set_profiling_enabled(true)` and `step_profile()`
provide opt-in timings for motion, broad phase, solve, and sleep without making
profiling part of the normal step cost. See
[`Benchmarks/Scale2D.sx`](Benchmarks/Scale2D.sx) and
[`Docs/Performance.md`](Docs/Performance.md) for the reproducible 1k/5k/10k
cases.

Forces, general shapes, joints, continuous collision detection, and application
plugins remain outside the current contract.

See [`Examples/World2D/FallingBody.sx`](Examples/World2D/FallingBody.sx) for the first
complete graphical consumer program. It emits dynamic squares into four fixed
walls and keeps the conversion between physical meters and rendered pixels in
the example.
