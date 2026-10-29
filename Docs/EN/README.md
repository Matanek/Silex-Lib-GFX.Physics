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

[`World settings and counters`](WorldSettings.md) documents creation choices,
runtime tuning, explicit substeps, wake policies, and logical scene counters.
See [Use pixels or centimeters](Units.md) to convert application coordinates.
See [Application and Scene3D integration](Application3D.md) for the optional
fixed-step 3D plugin and ECS body binding.
See [Find a game object](ApplicationIdentity.md) to associate application keys with physics objects.
See [Owning world and lifetime](WorldOwnership.md) for explicit world composition.

`World2D` owns every body. Destroying a body invalidates every copy of its
opaque `RigidBody2D` handle; subsequent access fails explicitly. `is_valid()`
allows code that retains handles across world updates to discard an invalid
reference without learning its internal slot or generation.

Collision geometry is also available without creating a world:

The [standalone 3D convex geometry](Geometry3D.md) exposes spheres, oriented
boxes, capsules, rigid poses, and distance, overlap, and ray queries. The
[3D world](World3D.md) moves bodies, resolves initial multiple contact points,
and sleeps small resting islands.

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

Custom filtering and pre-solve are opt-in per collider. They run on the thread
that owns `step`, before solver workers, and return explicit value decisions.
See [`Docs/ContactPolicies.md`](ContactPolicies.md) and
[`Tests/Consumer/Tests/ContactPolicies.sx`](../../Tests/Consumer/Tests/ContactPolicies.sx).

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

Applications may delegate fixed stepping, ECS lifecycle, Scene2D transform
authority, and completed event aggregation to the optional
[`Plugins.Physics2D` integration](ApplicationIntegration.md).

The reusable physics debug snapshot renders shapes, joints, contacts, bounds,
mass centers, islands, and constraint colors through Canvas or Scene2D without
native callbacks. See [`Docs/DebugDraw.md`](DebugDraw.md).

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
velocity integration, warm start, one biased sweep, position integration,
and one unbiased relaxation sweep. Both sweeps solve friction; restitution
and cache storage follow the substeps. A load threshold
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
constraint data; limits, motors, springs, targets and offsets remain readable
and mutable through the corresponding typed handle. Completed-step reactions
and tagged enumeration by world or body preserve introspection without exposing
solver state. Destroying either
attached body invalidates its joints. Contacts and joints share one deterministic
color graph, including the same parallel dispatch threshold for large
conflict-free colors. See [`Docs/Joints.md`](Joints.md) and
[`Tests/Consumer/Tests/Joints.sx`](../../Tests/Consumer/Tests/Joints.sx).

`CharacterMover2D` calculates bounded capsule motion against living colliders,
including initial depenetration, slopes, corners, and kinematic platforms,
without mutating the world. See [`Docs/CharacterMover.md`](CharacterMover.md)
and the interactive [CharacterMover2D application](https://github.com/Matanek/Silex-Examples/blob/main/Sources/CharacterMover2D.sx).

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
The executable parity boundary and every covered, divergent or excluded Box2D
capability are documented in
[`Docs/Completeness.md`](Completeness.md).

`World2D` resolves circle, capsule, segment, rounded-polygon and compound
contacts through the same persistent Soft Step path. Every sufficiently fast
dynamic convex collider also sweeps against fixed and kinematic geometry;
ordinary bodies do not silently opt into the additional dynamic-target cost,
which remains reserved for bullets.

[Rotating physics container](https://github.com/Matanek/Silex-Examples/tree/main/Sources/Physics2D/RotatingPhysicsContainer)
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
silex run Silex-Examples/Sources/Physics2D/RotatingPhysicsContainer/Main.sx --release
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

The [3D character mover](Character3D.md) moves a capsule with slopes, stairs and sliding.

The [3D hinge](Hinge3D.md) connects two bodies around an axis with hard stops and a torque-limited velocity motor.

The [3D fixed attachment](Fixed3D.md) preserves all six degrees of two bodies’ relative pose, with current-assembly capture, mutable local frames and force/torque reactions.

The [3D slider](Slider3D.md) guides a carriage along a rotating rail with signed travel and mutable rigid stops.

The [slider motor](SliderMotor3D.md) drives a relative speed with bounded force, braking and mutation.

The [slider friction brake](SliderFriction3D.md) slows travel without a motor using mutable maximum force.

[Signed force bounds](SliderForceBounds3D.md) set different effort in each direction, in velocity and position modes.

[Soft slider stops](SliderSoftLimits3D.md): load compression, damped spring, equal bounds and mutation.

The [slider position servo](SliderPosition3D.md) targets travel with a physical damped spring and bounded force.

The [hinge position motor](HingePosition3D.md) targets an angle with stiffness, damping and bounded torque.

The [hinge friction brake](HingeFriction3D.md) slows an unpowered axis with bounded, mutable torque.

[Signed torque bounds](HingeTorqueBounds3D.md) permit different effort in each direction, in velocity or position mode.

[Soft hinge stops](HingeSoftLimits3D.md) cushion angular overshoot with mutable physical stiffness.
[Combined control](HingeCombined3D.md) follows an angle and velocity updated together.

## Tile maps

[Tile map collisions](TileMap2D.md)

[Follow a moving target with position and velocity](SliderCombined3D.md).

[3D cone joint](Cone3D.md).

[3D swing and twist](SwingTwist3D.md).

[Six degrees of freedom](SixDOF3D.md).

[3D gear](Gear3D.md): signed ratio, tracked phase and torques on both bodies.

[3D rack and pinion](RackAndPinion3D.md): signed rotation/travel ratio, phase, torque and force.

[3D pulley](Pulley3D.md): fixed points, weighted length, slack and anchor reactions.

[3D path guidance](Path3D.md) follows a Hermite curve in meters with motors, friction and orientation transport.

A [hinged rail carrying a moving carriage](HingedRail3D.md) transmits the radial load to a dynamic support, with free rotation or a bounded motor.

[Hold a loaded rail and release a contact](LoadedRail3D.md): weight support, bounded motor effort and reversal against a wall.

[Carry a load through two perpendicular hinges](SpatialHinges3D.md): weight, off-plane torques and reversal under load.

[Bring a spatial chain into contact with a plane](SpatialContacts3D.md): contact, impulse moment and release.

[Compose a motorized shoulder and elbow](ArticulatedPose3D.md): four servos, transmitted load and moving frames.

[Create a ragdoll assembly and manipulate its pose](Ragdoll3D.md): hierarchy, body offsets, independent instances, parent/child filtering and motorized tracking.

[Rest a chassis on four wheel suspensions](VehicleSuspension3D.md): ray or swept-sphere supports, springs, stops, jumping and support reactions.

[Roll tires and resist drift](PassiveTires3D.md): inertia, rotation, friction curves and support reactions.

[Steer and brake a vehicle](VehicleControls3D.md): persistent controls, steering limits and service/hand brakes.

[Power the wheels](VehiclePowertrain3D.md): engine, clutch, automatic/manual transmission and differentials.

[Reduce body roll with paired suspension bars](VehicleAntiRoll3D.md).

[Limit total chassis inclination](VehicleTiltLimit3D.md).

[Two-track vehicle: driving, pivoting and braking](TrackedVehicle3D.md).

[Balance and steer a motorcycle](Motorcycle3D.md).

- [Physical 3D character](PhysicalCharacter3D.md)

- [Registered virtual character](VirtualCharacter3D.md)

- [Character mode selection and qualification](CharacterQualification3D.md)

- [Editing a height terrain](HeightField3D.md)

- [Terrain and constraint assembly qualification](TerrainConstraintQualification3D.md)

- [Parallel 3D simulation](Parallel3D.md): workers, deterministic ordering and world access.
