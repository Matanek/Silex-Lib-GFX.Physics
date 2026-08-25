# GFX.Physics

`GFX.Physics` is the optional physics extension for GFX. It begins with a
small, headless 2D simulation API and grows through executable examples.

```text
silex install GFX.Physics
```

```silex
use GFX.Physics
use STD.Math

var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.25))
    ..position = Math.Vec2(0.0, 10.0)
    ..rotation = 0.15
    ..friction = 0.75
)

world.step(1.0 / 60.0)
print(body.position())

world.destroy_rigid_body(body)
assert(!body.is_valid())
```

`World2D` owns every body. Destroying a body invalidates every copy of its
opaque `RigidBody2D` handle; subsequent access fails explicitly. `is_valid()`
allows code that retains handles across world updates to discard an invalid
reference without learning its internal slot or generation.

Collision geometry is also available without creating a world:

```silex
let capsule = Physics.ShapePlacement2D(
    Physics.Shape2D.capsule(Physics.Capsule2D(
        Math.Vec2(0.0, -0.5),
        Math.Vec2(0.0, 0.5),
        0.25
    ))
)
let wall = Physics.ShapePlacement2D(
    Physics.Shape2D.box(Physics.Box2D(Math.Vec2(1.0, 4.0), 0.1)),
    Physics.Transform2D(position:Math.Vec2(2.0, 0.0))
)
let hit = Physics.Geometry2D.shape_cast(
    capsule,
    Math.Vec2(4.0, 0.0),
    wall
)
```

This stateless layer supports boxes, circles, capsules, convex and rounded
polygons, segments, one-sided chains, filters, distances, overlaps, manifolds,
ray casts, and shape casts. Independent read queries can run concurrently. See
[`Docs/Geometry.md`](Docs/Geometry.md) and the executable
[`Examples/Geometry2D/Queries.sx`](Examples/Geometry2D/Queries.sx).

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
Euler step. Oriented boxes and circles can be fixed or dynamic. Box-box,
circle-box, and circle-circle contacts use an iterative impulse solver with the
appropriate inertia, restitution, and Coulomb friction. Boxes remain the
default shape when `shape` is omitted, preserving existing consumers.

A balanced dynamic AABB tree with fat proxies handles general shapes. Dense
circle scenes switch to a reusable uniform grid for circle-circle candidates
while retaining the tree for the fixed container and mixed shapes. Contact
impulses persist across steps and warm-start the next solve. Dynamic
circle-circle contacts use a compact constraint representation; general and
compact constraints retain one deterministic Gauss-Seidel order. Dense-circle
position correction applies a relaxed correction through eight retained-contact
passes and eight global grid sweeps. Each projection is capped relative to the
smaller collider, so a deep contact cannot move a body through several
neighbours in one pass. The global passes catch newly introduced overlaps
without transferring an entire penetration into the next neighbour.
General-contact islands sleep atomically after their residual surface motion
remains below the stability thresholds. The dense-circle path audits current
overlap and rests each quiet, supported body independently, so one noisy ball
does not keep an entire pile awake. Fast awake circles are swept against the
sleeping-circle grid before discrete contact generation, preventing a ball that
travels farther than its diameter in one step from entering the pile. Contact
wake decisions use one state snapshot and newly awakened bodies cannot
recursively wake the next support layer during their initial settling interval.

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
[`Benchmarks/CircleScale2D.sx`](Benchmarks/CircleScale2D.sx), plus
[`Docs/Performance.md`](Docs/Performance.md) for the reproducible 1k/5k/10k
cases. The reconstruction corpus and pinned Box2D oracle are documented in
[`Docs/OracleAndBudgets.md`](Docs/OracleAndBudgets.md).

The existing `World2D` regression solver still accepts only boxes and circles;
the additional forms currently belong to the stateless geometry API. Forces,
joints, persistent contacts for those forms, general-purpose continuous dynamic
collision response, and application plugins remain outside the current world
contract. The public shape cast is a geometry query, while the dense-circle
sweep described above remains narrower than general solver CCD.

See [`Examples/World2D/FallingBody.sx`](Examples/World2D/FallingBody.sx) for the
complete graphical consumer program. Its interactive emitter is currently
capped at 3,000 small dynamic circles, while explicit stress controls can still
prepopulate as many as 5,000. The fixed 60 Hz simulation runs on one persistent
worker while rendering remains independent, and its reusable
`BodyTransformBuffer2D` transfers all dynamic transforms without allocating a
handle object per body and frame.
