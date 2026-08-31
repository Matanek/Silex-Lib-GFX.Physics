# GFX.Physics

`GFX.Physics` is the optional native Silex physics extension for GFX. Its
headless 2D world uses one deterministic reconstruction based on the Box2D 3
algorithmic model; no external engine is linked into applications.

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
[`Docs/Geometry.md`](Geometry.md) and the public consumer proofs under
[`Tests/Consumer/Tests/Geometry.sx`](../../Tests/Consumer/Tests/Geometry.sx).

Living-world AABB, overlap, ray, and shape queries return stable collider
handles through caller-owned buffers, `any`, and `closest` intentions. See
[`Docs/WorldQueries.md`](WorldQueries.md) and
[`Tests/Consumer/Tests/WorldQueries.sx`](../../Tests/Consumer/Tests/WorldQueries.sx).

`World2D` also retains collision pairs and manifolds across steps. The current
snapshots can be read without exposing their cache identity:

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)
print(world.contact_count())
```

[`Tests/Consumer/Tests/Contacts.sx`](../../Tests/Consumer/Tests/Contacts.sx) proves
contact creation, persistence, invalidation and ordering. See
[`Docs/Contacts.md`](Contacts.md) for filters and the current solver
boundary.

Bodies can also own zero, one, or several stable `Collider2D` handles. Each
collider carries its geometry, density, typed material, collision filter,
sensor state, and event options; fixed chains may select one common material or
one material per segment. The existing body-level shape and material fields
remain an exact one-collider shortcut. See
[`Docs/Colliders.md`](Colliders.md) for creation, mutation, destruction,
invalidation, and the current response boundary.

Existing 0.4 world and body usage remains source-compatible across the switch.
The intentional solver and lifetime changes are listed in
[`Docs/Migration.md`](Migration.md).

Bodies derive composed mass, center of mass, and rotational inertia from their
colliders. They expose forces, torques, impulses, coordinate conversions,
fixed rotation, activation, runtime damping and sleep controls, and kinematic
transform targets. See [`Docs/BodyControl.md`](BodyControl.md) and the public
proofs in
[`Tests/Consumer/Tests/BodyControl.sx`](../../Tests/Consumer/Tests/BodyControl.sx).

Bullets, sensors, and opt-in post-step movement, contact, hit, and sensor
streams complete the gameplay feedback loop without worker callbacks. A bullet
extends continuous collision to dynamic targets; sensors retain filtering but
never produce physical response. See
[`Docs/EventsAndCCD.md`](EventsAndCCD.md) and the public consumer proofs in
[`Tests/Consumer/Tests/Events.sx`](../../Tests/Consumer/Tests/Events.sx).

Filtered radial explosions apply one bounded impulse per dynamic body and can
write deterministic body, point, and impulse results into a caller-owned
buffer. See [`Docs/Explosions.md`](Explosions.md) and
[`Tests/Consumer/Tests/Explosions.sx`](../../Tests/Consumer/Tests/Explosions.sx).

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
Euler step. Oriented boxes and circles can be fixed, kinematic, or dynamic.
Kinematic bodies follow their prescribed linear and angular velocities without
gravity or impulse response, while their surface velocity moves and wakes
dynamic contacts. Box-box, circle-box, and circle-circle contacts use an
iterative impulse solver with the appropriate inertia, restitution, and
Coulomb friction. Boxes remain the default shape when `shape` is omitted,
preserving existing consumers.

A balanced dynamic AABB tree retains fixed-shape queries. Worlds with dynamic
shapes use the same reusable deterministic grid regardless of worker count, so
parallelism cannot change the candidate set. Contact impulses persist across
steps and warm-start the next solve. General and compact circle constraints are
colored by body conflict and execute one common four-substep Soft Step graph:
velocity integration, warm start, two alternating biased sweeps, position
integration, normal relaxation, restitution, and cache storage. A load threshold
may dispatch a color to workers but never selects a historical solver.
Joint and non-primitive general-shape islands sleep atomically after their
residual surface motion remains below the stability thresholds. Primitive box
and circle contacts rest each quiet body independently, so one noisy surface
region does not keep an entire mixed pile awake. The dense-circle path also
audits current overlap before sleep. Fast awake circles are swept against the
sleeping-circle grid before discrete contact generation, preventing a ball that
travels farther than its diameter in one step from entering the pile. Contact
wake decisions use one state snapshot and newly awakened bodies cannot
recursively wake the next support layer during their initial settling interval.
Awake bodies and their deterministic islands are packed into reusable
contiguous ranges, so sleeping bodies leave the integration hot path. See
[`Docs/Islands.md`](Islands.md),
[`Tests/Consumer/Tests/Islands.sx`](../../Tests/Consumer/Tests/Islands.sx), and the
dense-pile regressions in [`Tests/World2D.sx`](../../Tests/World2D.sx).

`World2D` also owns typed distance, filter, motor, mouse, prismatic, revolute,
weld, and wheel joints. World-space anchors and axes become private local
constraint data; limits, motors, springs, and completed-step reaction forces
remain observable through the corresponding typed handle. Destroying either
attached body invalidates its joints. Contacts and joints share one deterministic
color graph, including the same parallel dispatch threshold for large
conflict-free colors. See [`Docs/Joints.md`](Joints.md) and
[`Tests/Consumer/Tests/Joints.sx`](../../Tests/Consumer/Tests/Joints.sx).

Large moving worlds can opt into the persistent STD worker pool:

```silex
world.enable_parallelism(4)
```

Large conflict-free colors then partition the same contact kernel into disjoint
worker ranges; smaller colors run directly to avoid scheduling overhead.
`set_profiling_enabled(true)` and `step_profile()`
provide opt-in timings for motion, broad phase, solve, and sleep without making
profiling part of the normal step cost. See
the centralized
[PhysicsWorldScale2D](https://github.com/Matanek/Silex-Benchmarks/blob/main/Sources/PhysicsWorldScale2D.sx)
and the internal [`Benchmarks/CircleScale2D.sx`](../../Benchmarks/CircleScale2D.sx), plus
[`Docs/Performance.md`](Performance.md) for the reproducible 1k/5k/10k
cases. The reconstruction corpus and pinned Box2D oracle are documented in
[`Docs/OracleAndBudgets.md`](OracleAndBudgets.md).
The executable parity boundary and every currently covered, partial, planned,
divergent or excluded Box2D capability are documented in
[`Docs/Completeness.md`](Completeness.md).

The existing `World2D` regression contact solver still resolves only unrounded boxes
and circles. Additional forms can be attached to the world and produce
persistent geometric contacts, but do not receive impulses or positional
correction yet. Continuous response for every ordinary dynamic pair and
application plugins remain outside the current world contract. The public
shape cast is also the geometry foundation of bullet CCD;
ordinary bodies do not silently opt into its dynamic-target cost.

[Rotating physics container](https://github.com/Matanek/Silex-Examples/tree/main/Sources/RotatingPhysicsContainer)
is the recommended visual introduction: it progressively reveals 120 circles and
boxes of varied sizes at deterministic randomized positions inside the
container. Each new element follows the rotating local frame while
`GFX.Animation` fades and scales it from zero, then becomes a dynamic physics
body. The thick four-wall kinematic container keeps turning by successive
45-degree steps in the same direction, driven by a second looping animation
timeline. Synchronized presentation and fixed-step transform interpolation keep
the container, animated previews, and simulated bodies visually aligned between
60 Hz physics updates.

```text
silex run Silex-Examples/Sources/RotatingPhysicsContainer/Main.sx --release
```

[FallingBodies2D](https://github.com/Matanek/Silex-Benchmarks/tree/main/Sources/FallingBodies2D)
is the integrated graphical stress consumer. Its interactive emitter is
capped at 3,000 small circles and boxes, while explicit stress controls can
still prepopulate as many as 5,000. The fixed 60 Hz simulation runs on one
persistent worker while rendering remains independent, and its reusable
`BodyTransformBuffer2D` transfers all dynamic transforms without allocating a
handle object per body and frame. Interactive runs use synchronized presentation
by default; performance measurements can opt into immediate presentation with
`--immediate`.
