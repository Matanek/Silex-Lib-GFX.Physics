# GFX.Physics architecture

`GFX.Physics` is an optional child package of GFX and owns the
`GFX.Physics` namespace. It depends on GFX as its authorized parent while its
simulation remains usable without a window, renderer, scene, or ECS world.

The public API expresses physical intentions. Numerical integration, storage,
spatial acceleration, contact generation, and solver data remain private.

The portable principal module contributes the package-owned `RigidBody2D` and
`World2D` declarations to the parent `GFX.Components` and `GFX.Resources`
catalogs. This changes only their public façade names: no implementation is
merged into GFX, and catalog collisions remain compiler errors.

The switched native Silex core contains:

- `Physics.World2D`, the owner and clock boundary of a 2D simulation;
- `Physics.RigidBody2D`, a body created and retained by that world;
- `Physics.RigidBody2DSettings`, its fixed, kinematic, or dynamic behavior,
  initial motion, rotation, mass, friction, damping, and response to gravity;
- `Physics.Collider2D` and `Physics.Collider2DSettings`, the stable per-body
  geometry, density, material, filter, sensor, and event boundary;
- `Physics.PhysicsMaterial2D` and its typed application identifier,
  including common or per-segment chain material selection;
- `Physics.Shape2D`, the explicit choice between box, capsule, chain, circle,
  convex polygon, and segment;
- `Physics.Box2D`, an oriented and optionally rounded rectangle retained as
  the default world shape;
- `Physics.Circle2D`, a circle with positive radius;
- `Physics.Capsule2D`, `Physics.Polygon2D`, `Physics.Segment2D`, and
  `Physics.Chain2D`, the additional stateless geometry forms;
- `Physics.Geometry2D`, the pure distance, overlap, manifold, ray-cast, and
  shape-cast boundary over transformed and filtered placements;
- `Physics.BodyTransformBuffer2D`, reusable structure-of-arrays output for
  bulk synchronization with a renderer or ECS;
- value snapshots for opt-in movement, contact begin/end/hit, and sensor
  begin/end streams collected after `World2D.step`;
- typed distance, filter, motor, mouse, prismatic, revolute, weld, and wheel
  joints created and owned by `Physics.World2D`.

Body handles keep the direct public API while `World2D` stores hot body fields
in parallel dense arrays: positions, velocities, inverse masses, inertias,
rotations, material properties, and sleep state. Stable sparse slots map each
opaque handle to its current dense index. Destruction increments the slot
generation, compacts the dense arrays by moving their last entry, and makes a
stale handle fail explicitly. Freed slots are reused without revalidating any
older copy of a handle. Neither slot, dense index nor generation leaks into the
public contract.

World colliders use their own generational dense pool. A body owns a private
linked set of collider slots, so body compaction does not move or expose
collider identities and body destruction invalidates all of its colliders.
Collider topology mutations mark derived world data dirty; the broad phase,
candidate cache, sensor pairs, and event counters are rebuilt before the next
step. The retained public `shape()` accessor still reports the primary box or
circle used by the regression solver and fails explicitly for an empty body.
The broader `Shape2D` vocabulary is accepted by `ShapePlacement2D` for pure
geometry queries and by `World2D` for persistent contacts. Every valid rigid
shape family now enters the same dynamic-response solver.

The stateless geometry layer expands each form into one or more private convex
proxies. Polygon construction computes a welded convex hull. GJK produces
closest witnesses; conservative advancement drives ray and shape casts; face
axes produce manifolds with at most two clipped points. Chain segments keep
the Box2D winding convention and accept queries only from their right side.
Filters are evaluated at the public query boundary. Every temporary simplex,
axis, and candidate belongs to one call, which permits parallel read queries
without locks or world-step state.

World queries traverse living colliders and write handles ordered by creation
identity into consumer buffers. Their query filter remains distinct from
contact filtering; AABB, shape overlap, ray cast, and shape cast expose no
proxy or internal traversal order. Each call owns its temporary values, so
multiple readers may share a resting world while `step` locks this boundary.

`CharacterMover2D` composes world overlaps and shape casts around a capsule.
Plane collection, bounded iterative solving, and gameplay state application
remain separate. Calculation mutates neither world nor bodies and returns a
value for the consuming controller to apply.

These algorithms are native Silex adaptations informed by Box2D `v3.1.1` at
commit `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`, notably `src/hull.c`,
`src/distance.c`, `src/geometry.c`, and `src/manifold.c`. Box2D is Copyright
(c) 2022 Erin Catto under the MIT License and remains a benchmark-only oracle.
Private GJK vertices are reference-backed as a temporary workaround for a
Silex Release-backend discrepancy in nested mutation of structs held by a
collection; the public API remains value-like.

The established broad-phase, contact, and solver invariants remain regression
oracles while their internal algorithms evolve.
After a public body destruction, their derived indices and reusable buffers are
rebuilt from the surviving dense body state; ordinary stepping then continues
without preserving a pair or contact that referenced the removed body.

General-shape and compound-body world contacts reuse that lifecycle and enter
the dynamic-response path. Compound broad-phase bounds union every
collider, while narrow-phase filtering and sensor discovery use each collider's
own filter and flags. The
broad phase retains stable candidate slots; a general pair refreshes its
manifold in place and clears the slot when the shapes separate. Public
`Contact2D` values are read-only snapshots reconstructed in stable body-slot
order, so BVH nodes, pair hashes, dense indices, and cached impulses do not
cross the API boundary.

Sensors retain the geometry and collision-filter path but never enter contact
islands or the impulse solver. Their overlap pairs and all other event streams
are deterministic completed-step buffers, not callbacks. Event storage uses
reusable value arrays and creates opaque body handles only when consumer code
reads an event. Movement, solid contact, hit, and sensor streams are opt-in so
an ordinary world does not construct unused payloads.

Continuous motion keeps two costs distinct. Fast ordinary dynamic bodies sweep
every public convex collider against fixed and kinematic geometry; rotational
motion refines the first swept overlap and kinematic targets contribute their
relative sweep. Bodies created with `is_bullet` additionally test dynamic
targets. Sensor hits emit transitions without response. Slow bodies return
before pair traversal.

Kinematic bodies retain zero inverse mass and inertia, so contacts never alter
their prescribed motion. `World2D.step` advances their linear and angular
velocities before contact generation, excludes them from gravity and sleep,
and exposes their surface velocity to dynamic contact response. They share the
non-dynamic broad-phase set with fixed bodies but keep their previous transform
for continuous sweeps and opt-in movement events.

Worker count never selects a different broad phase or solver. Worlds with
dynamic shapes use the same reusable deterministic grid for one or several
workers; the tree remains the fixed-shape query structure. This keeps
candidate sets, insertion order, and contact-cache evolution identical across
worker counts.

The general solver separates every circle, capsule, segment, convex or rounded
polygon, and one-sided chain-segment pairing. Oriented boxes retain their four
specialized face axes, circle-box contacts use the box's local frame, and
circle-circle contacts use their center axis and combined radius. Corner-to-face
impacts use one estimated contact point. Parallel faces use two endpoints of
their shared interval and solve both normal impulses as a coupled 2×2 system;
friction is then applied at each endpoint. Effective normal and tangent masses,
the coupled matrix, and combined friction are prepared once in a contiguous
constraint array and reused through all velocity iterations. Candidate pairs
retain contact anchors plus normal and tangent impulses across steps;
geometrically compatible contacts warm-start the next solve while moved or
separated contacts invalidate their cache instead of injecting stale torque.
The touched collider or chain segment supplies friction, restitution, tangent
surface speed, and rolling resistance.

The solver prepares general contacts and a compact dynamic-circle form, then
places every constraint into deterministic conflict-free colors. Four true
substeps run by default; callers can choose another positive count per step.
Each substep integrates velocities, warm-starts, runs two alternating biased
color sweeps, integrates positions, and performs one normal-only relaxation
sweep. Friction runs on the second biased sweep; restitution and impulse-cache
storage follow the substeps. World settings control the physical contact
tuning and speed limits without exposing this schedule. One worker calls the
same jobs directly, while a large color partitions the same kernel across the
persistent executor. The twelfth overflow color remains explicitly ordered
and scalar.

The former discrete impulse backend and its warm-start path are not retained
as a fallback. The colored Soft Step graph above is the only contact solver;
worker and load thresholds change execution partitioning, never semantics.

Joints use a separate generational dense store behind their typed public
handles. Creation converts world anchors and axes to local body data; body
compaction therefore cannot invalidate a live constraint. Destroying a body
first destroys every attached joint, while explicit joint destruction advances
its own generation. Contact colors claim body masks first, then joint rows join
the same twelve-color schedule. Warm start, biased sweeps, integration, and
relaxation execute contacts and joints per color before advancing to the next
color. The scalar overflow rule and 4,096-entry worker threshold are shared.
Joint edges also enter the sleep union-find, and wake state propagates through
an articulated component before active bodies are packed.

Compact circle collisions are immutable during the solve; their normal,
tangent, and accumulated restitution impulses live in a smaller mutable list.
Groups of four normal constraints expose pairwise ARM64 SIMD opportunities
without changing their scalar semantics. General parallel faces retain their
coupled 2×2 normal solve and clipped per-point separations. There is no legacy
positional projection phase hidden behind a worker-count or load threshold.

Bodies ready to sleep receive a final overlap audit from current AABBs, and
sleeping bodies are not translated afterward. Primitive box and circle contacts
sleep locally, allowing quiet depth to leave the hot path while the pile surface
remains active; joint and non-primitive general-shape islands retain atomic
sleep. Cached impulses record the awake state of both bodies and are discarded
across every sleep/wake transition, preventing an old stack load computed for
different effective masses from being released into a neighbour.

Before that narrow phase, a reusable deterministic grid discovers candidates
from tight bounds for every world containing dynamic shapes. A custom
open-addressed pair set deduplicates persistent candidates, and stable ordering
keeps pair insertion and cache evolution independent of worker count. The
package-private dynamic AABB tree remains the fixed-shape query structure; it
is not selected as a second dynamic-world algorithm when parallelism is enabled.

Before discrete dense-circle contact generation, fast awake circles query a
second grid containing only sleeping circles. A segment-circle intersection
clips the moving centre to its earliest contact whenever one fixed step would
carry it through a sleeping support. This targeted continuous test prevents the
slow-emission case from tunnelling into an already settled pile without
substepping the whole world. The general swept path described above covers
fixed and kinematic targets, mixed convex shapes, chains, and rotation;
bullets alone extend it to dynamic targets.

Parallelism is explicit at the world boundary. `enable_parallelism` creates a
persistent STD executor. The common stage graph dispatches body ranges only at
16,384 active bodies and conflict-free constraint colors at 4,096 entries;
smaller jobs execute directly to avoid measured scheduling regressions. These
thresholds select execution mode, never a different solver. The steady-state
step does not allocate per contact or per job.

At the beginning of each step, awake dynamic bodies are gathered by stable body
slot into a reusable contiguous list. Serial integration walks only that list;
parallel integration partitions the same logical order into disjoint ranges.
Sleeping data therefore leaves the motion hot path without making worker count
observable.

General-shape and joint sleep is evaluated from a graph rebuilt
deterministically after each solve. A reusable union-find groups touching awake
non-primitive dynamic bodies and articulated bodies that allow sleep. The
lowest stable body slot is always the root, then a second reusable layout packs
the bodies of each island contiguously in root and body identity order. Retained
general contacts participate in this graph even before their dynamic response
is enabled.
Per-body timers use the linear velocity plus the angular surface motion: they
advance below 5 cm/s, erode slowly between 5 and 10 cm/s, and reset above
10 cm/s. Small islands require every body to validate 0.5 seconds of rest. In a
dense general-shape island, 95 percent must validate that delay and no body may
exceed the hard motion threshold; the complete island then sleeps atomically.

Primitive box and circle contacts instead sleep each quiet body independently.
This prevents a handful of noisy surface bodies from holding thousands of
supported bodies awake. The dense-circle grid additionally validates current
local overlap before sleep. A dynamic body with sleep disabled forms an
activity boundary instead of blocking unrelated resting bodies. A sleeping
body acts as a fixed support until a meaningful relative impact wakes it.
Primitive-contact wake decisions are collected from one immutable awake-state
snapshot before active pairs are filtered. The newly awakened surface body
therefore receives its sleeping support contacts in the same step, while a
0.5-second propagation cooldown prevents that wake from walking downward one
layer per frame. Slow positional correction moves the
awake body against the rigid support without restarting an entire compressed
pile.

`World2DStepProfile` is an opt-in observable diagnostic, not solver plumbing. It
reports the four stable phases `motion_ms`, `broad_phase_ms`, `solve_ms`, and
`sleep_ms`, plus their total. Internal tree, contact, constraint, and task types
remain package-private.

Every following capability must first appear in a focused executable example
and a consumer-facing test. Application integration, cloth, soft bodies,
fluids, and 3D are intentionally outside the current contract. Dense contact
and joint solving already share the
conflict-free constraint graph and worker pool. Additional SIMD kernels likewise
depend on a
portable vector surface in the Silex backend; the current SoA and contiguous
constraint layouts are prepared for that work without exposing it publicly.
