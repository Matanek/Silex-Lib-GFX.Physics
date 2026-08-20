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
- `Physics.Box2D`, an oriented rectangle used by the initial collision solver.

Body handles keep the direct public API while `World2D` stores hot body fields
in parallel arrays: positions, velocities, inverse masses, inertias, rotations,
material properties, and sleep state. The broad-phase tree similarly separates
its topology fields while retaining contiguous AABBs. Neither internal index nor
generation leaks into the public contract.

The solver separates oriented boxes on their four face axes. Corner-to-face
impacts use one estimated contact point. Parallel faces use two endpoints of
their shared interval and solve both normal impulses as a coupled 2×2 system;
friction is then applied at each endpoint. Effective normal and tangent masses,
the coupled matrix, and combined friction are prepared once in a contiguous
constraint array and reused through all velocity iterations. Candidate pairs
retain contact anchors plus normal and tangent impulses across steps;
geometrically compatible contacts warm-start the next solve while moved or
separated contacts invalidate their cache instead of injecting stale torque.

Penetration correction is a separate two-pass positional solve. Each pass
revisits neighbouring constraints with a small slop and a bounded correction;
this avoids the energy ping-pong caused by projecting every overlap completely
during contact construction. Positional translations mark their broad-phase
transform dirty even when the body goes to sleep in the same step.

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

Parallelism is explicit at the world boundary. `enable_parallelism` creates a
persistent STD executor. Motion integration is partitioned by disjoint body
ranges. For 256 or more moved proxies, pair discovery uses two parallel tree
passes: one count per proxy, a sequential prefix sum, then direct writes into
disjoint slices of one reusable pair buffer. The steady-state step does not
allocate per contact or per job.

Sleep is evaluated from a contact graph rebuilt deterministically after each
solve. A reusable union-find groups touching awake dynamic bodies that allow
sleep. Per-body timers use the linear velocity plus the angular surface motion:
they advance below 5 cm/s, erode slowly between 5 and 10 cm/s, and reset above
10 cm/s. Small islands require every body to validate 0.5 seconds of rest. In a
dense island, 95 percent must validate that delay and no body may exceed the
hard motion threshold; the complete island then sleeps atomically. This quorum
prevents a few solver-noise outliers from holding hundreds of visually settled
bodies awake without freezing an island that still contains meaningful motion.
A dynamic body with sleep disabled forms an activity boundary instead of
blocking unrelated resting bodies. A sleeping body acts as a fixed support
until a meaningful relative impact or penetration wakes it.

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
