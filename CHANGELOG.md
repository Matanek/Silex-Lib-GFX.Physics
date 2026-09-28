# GFX.Physics release notes

This log starts with 0.7.0 and covers changes since tag 0.6.0. Future changes
are recorded under `## [Unreleased]` before publication, with French authored
first in `CHANGELOG.fr.md`.

## [Unreleased]

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
  step; CCD remains to be delivered.
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
