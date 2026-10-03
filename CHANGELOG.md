# GFX.Physics release notes

This log starts with 0.7.0 and covers changes since tag 0.6.0. Future changes
are recorded under `## [Unreleased]` before publication, with French authored
first in `CHANGELOG.fr.md`.

## [Unreleased]

- 3D CCD closes the remaining gap between its search margin and the impact
  surface. An oblique convex bounce is resolved in the step that clips motion,
  without a sticking frame before the impulse.

- `ConvexHull3D(points)` adds an immutable solid hull and `Shape3D.convex`:
  signed sphere/convex distances, rays and collisions against a fixed body,
  with linear CCD, filters and sensors. Its triangulated boundary is available
  for rendering; moving hulls, compound children, box/capsule/convex pairs and
  CharacterMover3D remain unsupported and are rejected.

- Linear CCD respects front-facing fixed triangles and meshes: fast spheres,
  boxes and capsules pass through back faces and openings without clipped
  motion or phantom events. A nearby back face no longer hides the next
  front face; standalone queries remain bilateral. Tilted poses and a box
  compound child are qualified.

- Qualified open planar meshes: boxes, spheres and capsules fall through
  a hole, a wide box rests on its edges, and contact ends at the outer edge.
  Supports stay on existing faces.

- Boxes keep multiple surface contacts on terrain when their supports differ.
  Rest in a two-pan valley is qualified against Jolt Debug/Release, including
  reversed orders and a compound child. Identical reactions from coplanar
  triangles or a ridge are merged; each support keeps its face ID and events.
  Sensors expose the same surfaces without correction.

- Boxes support bilateral distance and overlap against fixed triangles and
  meshes. World contacts provide up to four support points across touching
  coplanar faces; diagonal rest and inclined sliding are qualified against
  Jolt Debug/Release. `BoxTerrainScene` combines a stack with grid traversal.
  Arbitrary folds and terrain CCD remain open. `RigidBody3D.same_body` reads
  its argument through a borrowed parameter, allowing direct comparisons of
  handles reached from borrowed state.

- Capsule–triangle and capsule–mesh distance and overlap cover the complete
  axial segment, oriented poses and both argument orders. World contacts use
  the front side; a capsule parallel to a flat face can rest on two points.
  `CharacterMover3D` traverses an inclined grid in both directions with
  continuous support and Jolt positions matched within 5 mm. `CapsuleTerrainScene`
  adds manual movement and jumping. Boxes on terrain remain outside this slice.

- `TriangleMesh3D.from_height_grid` builds a fixed surface from a regular
  grid of finite heights, with deterministic identities for both triangles
  in each cell. A sphere crosses multiple inclined seams in both directions
  on a 4 by 4 case compared with Jolt Debug and Release.

- A seam between two fixed triangles with a 0.4 m height difference is
  qualified in both directions for a frictionless sphere, with face identity
  and trajectory compared against Jolt Debug and Release.

- `TriangleMesh3D` combines triangles into a fixed shape. Distance and ray
  queries expose the triangle index; the world selects one front-facing
  triangle per dynamic sphere primitive or compound child. Crossing a flat two-triangle seam retains
  one support contact without duplicate correction.

- `Triangle3D` adds an orientable fixed physics surface. Standalone sphere
  distance and overlap and ray queries cover the face, edges, and vertices;
  the world responds to dynamic spheres from the front only. Other pairs,
  triangle compounds, and moving triangle bodies remain outside this slice.

- `RigidBody3D.set_shape` replaces a live body's shape, including a modified
  compound, without changing its identity. Dynamic mass is recalculated from
  density; previous contacts end on the next step and their impulses are not
  reused with the new geometry.

- 3D compounds are now dynamic, with full mass, center of mass, and inertia
  tensors derived from rotated and offset children. Contacts retain child
  identities. `MassProperties3D` accepts a `Mat3` for non-diagonal inertia
  while preserving existing `Vec3` calls.

- `CharacterMover3D` now follows a kinematic support through translation or
  rotation using its previous pose and body identity. The result exposes the
  supporting body through `support()`; jumping, removal, disabling, and query
  filtering end the carry without residual motion.

- Capsule sliding no longer stalls on tilted faces and their edges when
  the projection residual is below the tangential movement threshold. Contact
  detection and plane clipping now use the same threshold. Stair lookahead also
  requires support at the edge contact height, preventing false step-ups onto
  lower ground beyond a rock.

- Stair climbing now respects requested horizontal travel: support lookahead
  beyond the capsule edge no longer causes a dash, even at low speed. The
  stair correction does not add vertical velocity from the sampled normal.

- `CharacterMover3D` adds virtual capsule motion: sliding, ceilings, slope
  limits, stairs, floor snapping and bounded penetration recovery. Input and
  jumping remain application decisions.

- Fixed and kinematic 3D compounds retain one manifold per touching child
  pair, with independent events and warm starting. Kinematic compounds can
  carry and wake dynamic bodies through translation and rotation.

- The 3D solver uses scalar tangent mass and zero normal torque for centered
  spheres with isotropic inertia. Offset centers of mass and anisotropic sphere
  inertia retain the general response. A private spatial grid finds neighbors
  in dense worlds, with conservative fallback for oversized shapes and
  coordinates outside the grid. Pair ordering, timestep, iteration counts and
  sleep thresholds are preserved.

- 3D warm starting reprojects friction onto the current tangent plane when
  the normal turns, avoiding an artificial support component. Sphere pairs
  use their centers and radii directly during detection and position correction,
  without rebuilding unnecessary placements and witnesses each iteration.
  Other shapes retain the general path; timestep and iteration counts are unchanged.

- 3D contacts cache body identities, reuse the previous-contact lookup for
  warm starting, and read its points without a temporary array. A linear
  merge of sorted contacts emits begin and end events while preserving
  their order and identities.

- The 3D broad phase walks sorted intervals directly instead of rebuilding
  an active array for each body. Candidate pairs, their order and contact
  tolerances are preserved.

- Isotropic inertia tensors (cubes, spheres or custom masses) apply their
  scalar factor directly, avoiding redundant rotations. Solver helpers borrow
  bodies during iterations to avoid repeatedly managing owned references.
  Inertia rounding changes slightly and can change chaotic trajectories.

- Reduce 3D contact and sleep overhead: build islands by joining contacts and
  constraints, use SAT separation alone for box position correction, and skip
  ineffective impulse calculations on fixed and kinematic bodies. Solver
  iteration counts and simulation frequency are preserved.

- Reduced the cost of 3D box columns with rotation-aware bounds, rejection
  of separated boxes before computing distance witnesses, and reuse of
  collision axes and invariant solver data. Iteration counts, friction and
  simulation timestep stay identical; public distance queries retain their
  exact witnesses. Seven paired macOS ARM64 Release runs measure
  29.36 → 12.71 ms/step for 256 boxes; the toppling scenario improves
  from 24.31 to 11.95 ms/step, excluding rendering.

- Faster loaded 3D worlds through a bounding-sphere sweep for candidate pairs
  and ordered lookup of persistent contacts. Iterative position correction
  keeps a 256-box column above the floor, while wake propagates through
  existing contacts. On macOS ARM64, 1,024 bin spheres improve from 27.82 to
  a median 11.67 ms per physics step without rendering; 256 boxes require
  28.80 ms per step.
- Added a damped spring to `DistanceConstraint3D`, configurable by frequency
  and damping ratio at creation or while simulating. Exact lengths and soft
  range limits are tested; free oscillation is compared with pinned Jolt in
  Debug and Release.
- Fixed spurious tangential velocity after a fast face-on, four-point impact
  by settling multi-point normal support before friction. The 3D scene's
  projectile no longer drifts upward after hitting the wall.
- Added an optional linear sweep for dynamic bodies to stop a fast sphere at
  a thin wall and report complete one-step sensor crossings. The wall stop
  is compared with pinned Jolt in Debug and Release; Jolt's missing fast
  sensor event is documented.
- Added pair filters with categories, masks, and groups, plus independent
  query filters. Sensor bodies emit overlap events without physical response;
  one complete passage is compared with pinned Jolt in Debug and Release.
- Added `World3D` queries for the nearest ray hit, sorted multiple hits, and
  shape overlaps, with body/child identity, one-body exclusion, and snapshots
  safe after destruction. A selection case is compared with pinned Jolt in
  Debug and Release.
- Added `PointConstraint3D` with two coincident local anchors and free
  rotation, reaction force, runtime changes, and safe lifetime. It shares
  contacts and sleep islands; a support and off-center pendulum are compared
  with pinned Jolt in Debug and Release.
- Added `DistanceConstraint3D` with local anchors between two bodies, a fixed
  length or rigid range, reaction force, runtime changes, and safe handle
  invalidation. It shares contact iterations and sleeping islands; the
  suspended body case is compared with pinned Jolt in Debug and Release.
- Fixed tilted box-to-box supports by clipping the incident face, excluding
  corners above the support, and reducing to four points. A contact's
  representative point is now the manifold centroid, avoiding a distant
  marker on a large floor.
- Added `Plugins.Physics3D`, `Components.PhysicsBody3D`, and frame-aggregated
  events to connect the 3D world to Application/ECS and Scene3D poses.
  Fixed stepping, pause, catch-up, and 2D/3D coexistence are verified
  headlessly; Silex-Examples includes a Scene3D demonstration.
- Added 3D contact begin and end events read after a step as stable
  `Contact3D` snapshots. Destruction queues an end for the next step;
  recycled bodies and child IDs remain distinct.
- Added immutable `Compound3D` to assemble spheres, boxes, and capsules on a
  fixed body. Distances, overlaps, rays, and contacts report the selected
  child ID. Dynamic compounds remain to be delivered.
- Added `Sphere3D`, `Box3D`, `Shape3D`, and `Transform3D` values as the first
  standalone 3D geometry primitives. Invalid dimensions, poses, and rotations
  are rejected. `Geometry3D` provides signed distances, overlaps, and rays for
  spheres and oriented boxes.
- Added an initial standalone `World3D`: fixed, kinematic, and dynamic bodies,
  sphere/box mass and inertia, forces, torques, impulses, free motion, and
  handles invalidated on destruction.
- Added an initial sphere/box contact response in `World3D`: normal impulse,
  penetration correction, and pair observations after stepping.
- Added per-body friction and restitution with contact observations. Sliding
  stays within a Coulomb impulse limit; restitution applies to sufficiently
  fast impacts.
- Nearly parallel box faces use multiple contact points, a solver shared by
  pairs, and impulses carried between steps. `Contact3D.write_points` exposes
  points and their impulses. A small stack remains stable at the tested fixed
  step; linear continuous collision is now optional and does not cover
  rotation.
- Added sleeping for dynamic bodies and contact islands, with wakeup from
  commands, collisions, or support changes. Sleep timing and command wakeup
  are compared with pinned Jolt in Debug and Release.
- Added vertical `Capsule3D` with mass and inertia, standalone distance,
  overlap and ray queries, and initial contacts with spheres, boxes, and
  capsules. Three capsule/box witnesses are compared with Jolt in Debug and Release.
- Added the `TileMapCollider2D` ECS component: one fixed body per map, merged solid rectangles, rebuilds on edits and integration with body activation.

## [0.7.0] - 2026-09-24

### Why upgrade?

This release extends application integration of physics worlds, strengthens
lifetime contracts, and fixes contacts and constraints. It also reduces
temporary copies and allocations in the solvers.

### Changes

- Physics stepping can be suspended without catch-up on resume or stale
  events; inactive ECS bodies retain their state.
- Character movement gains stop and slide responses, fixed-step hooks, and
  queries that exclude the character itself.
- Objects and snapshots can carry application identities. Completed-step
  counters and body identities are exposed; body-wide event options and
  subscription retention are strengthened.
- Compound-collider contacts remain independent. Speculative contacts,
  degenerate geometry, motor/mouse joints, and distance constraints are fixed;
  joint reactions respect their units.
- A zero-duration step is distinct from an explicit contact refresh. Retained
  handles are invalidated when the world is finalized, and invalid public
  values receive stronger checks.
- The solver borrows more body views and keeps velocities local across
  impulses. Worlds without joints skip unnecessary joint collision filtering
  and passes. Differential tests and parallel determinism traces cover more cases.

### Impact and migration

Review uses of zero-duration steps, events, handles after world destruction,
and joint observations: this release corrects their contracts, not just their
performance. Consult the relevant guides under `Docs/EN/`. Silex 0.47.0 is
recommended for recent runtime fixes and optimizations; the declared minimum
remains 0.44.0.

The [CCD allocation diagnostic](Benchmarks/Baselines/2026-09-24-native-heap.md)
measures a **compiler** improvement with an unchanged solver. Its figures do
not measure the overall gain of GFX.Physics 0.7.0 over 0.6.0.
