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

The first vertical slice contains:

- `Physics.World2D`, the owner and clock boundary of a 2D simulation;
- `Physics.RigidBody2D`, a body created and retained by that world;
- `Physics.RigidBody2DSettings`, its fixed or dynamic behavior, initial motion,
  rotation, mass, friction, damping, and response to gravity;
- `Physics.Shape2D`, the explicit choice between `box` and `circle`;
- `Physics.Box2D`, an oriented rectangle retained as the default shape;
- `Physics.Circle2D`, a circle with positive radius;
- `Physics.BodyTransformBuffer2D`, reusable structure-of-arrays output for
  bulk synchronization with a renderer or ECS.

Body handles keep the direct public API while `World2D` stores hot body fields
in parallel dense arrays: positions, velocities, inverse masses, inertias,
rotations, material properties, and sleep state. Stable sparse slots map each
opaque handle to its current dense index. Destruction increments the slot
generation, compacts the dense arrays by moving their last entry, and makes a
stale handle fail explicitly. Freed slots are reused without revalidating any
older copy of a handle. Neither slot, dense index nor generation leaks into the
public contract.

Shapes use their own generational dense pool. A body owns a private linked set
of shape slots, so body compaction does not move or expose shape identities and
body destruction releases all of its shapes. The retained public `shape()`
accessor still reports the primary box or circle used by the regression solver;
the additional shape capacity prepares the native core without prematurely
publishing the geometry API from the next reconstruction step.

The existing broad phase, contacts and solver remain the regression oracle.
After a public body destruction, their derived indices and reusable buffers are
rebuilt from the surviving dense body state; ordinary stepping then continues
without preserving a pair or contact that referenced the removed body.

The general solver separates oriented boxes on their four face axes and handles
circle-box contacts in the box's local frame. Circle-circle contacts use their
center axis and combined radius. Corner-to-face
impacts use one estimated contact point. Parallel faces use two endpoints of
their shared interval and solve both normal impulses as a coupled 2×2 system;
friction is then applied at each endpoint. Effective normal and tangent masses,
the coupled matrix, and combined friction are prepared once in a contiguous
constraint array and reused through all velocity iterations. Candidate pairs
retain contact anchors plus normal and tangent impulses across steps;
geometrically compatible contacts warm-start the next solve while moved or
separated contacts invalidate their cache instead of injecting stale torque.

The dense dynamic-circle path prepares a smaller one-contact constraint that
contains only the two body indices, normal, local contact anchor, cached
impulses, effective masses, precomputed tangent arms, velocity bias, and
friction. Per-body friction roots are also cached once, making the geometric
mean material mix a multiplication rather than a square root per contact.
Compact circle constraints and general
constraints share an encoded order array, so the eight velocity and sixteen
position iterations preserve deterministic Gauss-Seidel propagation without
paying the full general-contact footprint for every ball.

Penetration correction is a separate sixteen-pass positional solve. In a dense
dynamic-circle world, the first eight passes reuse the current contact set and
the final eight rebuild the uniform grid to catch contacts introduced by
earlier corrections. Circle penetration is relaxed per iteration: a full
correction moved one ball entirely into its next neighbour and could make a
dense pile collapse intermittently. Every iterative general, circle, and fixed
contact correction is additionally capped at one quarter of the smaller
shape's sweep radius; hard container recovery remains allowed to restore a body
that has already crossed a boundary. The former absolute 0.4 m cap was four
diameters in the graphical reference and could project a deeply engaged body
through several neighbours in one pass, producing a pile-wide decompression.
Near-coincident centres retain a
meaningful pre-step separation axis even when that preceding contact was
already penetrating; this preserves the physical entry direction against a
wall. A truly coincident resting degeneracy falls back to a deterministic
horizontal escape axis. Global grid sweeps alternate their traversal direction
to avoid leaving the same low-index boundary contact unresolved.
Bodies ready to sleep receive a final overlap audit from current AABBs, and
sleeping bodies are not translated afterward. Cached impulses record the awake
state of both bodies and are discarded across every sleep/wake transition,
preventing an old stack load computed for different effective masses from being
released into a neighbour.

Before that narrow phase, a package-private dynamic AABB tree stores one fat
proxy per body. Escaping proxies are removed and reinserted, while tree
rotations keep sequential insertions balanced. Candidate pairs persist between
steps, so only proxies that leave their fat bounds query the tree again. Tight
body bounds remove stale fat-proxy pairs before the iterative solver. Fat bounds
predict four times the current displacement to avoid needless reinsertion. A
custom open-addressed pair set deduplicates persistent candidates. Only newly
discovered candidates are ordered before insertion; a stable two-pass counting
sort reuses world-owned buffers instead of heap-sorting every active pair on
every step.

When the dynamic population is dominated by circles, a reusable hashed uniform
grid discovers circle-circle neighbours in the surrounding cells. Fixed bodies
and all box or mixed-shape queries remain in the AABB tree. This hybrid avoids
turning a dense ball pile into thousands of independent tree traversals while
preserving boxes as first-class colliders.

Before discrete dense-circle contact generation, fast awake circles query a
second grid containing only sleeping circles. A segment-circle intersection
clips the moving centre to its earliest contact whenever one fixed step would
carry it through a sleeping support. This targeted continuous test prevents the
slow-emission case from tunnelling into an already settled pile without
substepping the whole world. It is not general CCD: awake-awake, box, mixed
shape, and arbitrary swept rotation remain discrete.

Parallelism is explicit at the world boundary. `enable_parallelism` creates a
persistent STD executor. Motion integration is partitioned by disjoint body
ranges. For 256 or more moved proxies, pair discovery uses two parallel tree
passes: one count per proxy, a sequential prefix sum, then direct writes into
disjoint slices of one reusable pair buffer. The steady-state step does not
allocate per contact or per job.

General-shape sleep is evaluated from a contact graph rebuilt deterministically
after each solve. A reusable union-find groups touching awake dynamic bodies
that allow sleep. Per-body timers use the linear velocity plus the angular
surface motion: they advance below 5 cm/s, erode slowly between 5 and 10 cm/s,
and reset above 10 cm/s. Small islands require every body to validate 0.5
seconds of rest. In a dense general-contact island, 95 percent must validate
that delay and no body may exceed the hard motion threshold; the complete
island then sleeps atomically.

The dense-circle grid path instead validates each body against current local
overlap before sleeping it independently. This prevents a handful of noisy
surface circles from holding thousands of supported circles awake. A dynamic
body with sleep disabled forms an activity boundary instead of blocking
unrelated resting bodies. A sleeping body acts as a fixed support until a
meaningful relative impact wakes it. Circle wake decisions are collected from
one immutable awake-state snapshot before active pairs are filtered. The newly
awakened surface body therefore receives its sleeping support contacts in the
same step, while a 0.5-second propagation cooldown prevents that wake from
walking downward one layer per frame. Slow positional correction moves the
awake body against the rigid support without restarting an entire compressed
pile.

`World2DStepProfile` is an opt-in observable diagnostic, not solver plumbing. It
reports the four stable phases `motion_ms`, `broad_phase_ms`, `solve_ms`, and
`sleep_ms`, plus their total. Internal tree, contact, constraint, and task types
remain package-private.

Every following capability must first appear in a focused executable example
and a consumer-facing test. Forces, general shapes, constraints,
continuous collision detection, application integration, cloth, soft bodies,
fluids, and 3D are intentionally outside the current contract. Dense contact
parallel solving requires a conflict-free constraint graph (or coloring) before
it can safely use the worker pool. Explicit SIMD kernels likewise depend on a
portable vector surface in the Silex backend; the current SoA and contiguous
constraint layouts are prepared for that work without exposing it publicly.
