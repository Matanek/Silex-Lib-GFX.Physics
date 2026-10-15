# GFX.Physics release notes

This log starts with 0.7.0 and covers changes since tag 0.6.0. Future changes are recorded under `## [Unreleased]` before publication,
with French authored first in `CHANGELOG.fr.md`.

## [Unreleased]

- `WheeledVehicle3D` combines a dynamic chassis with ray-supported wheel suspensions, unilateral springs and compression stops. Support, length and force observations, dynamic support reactions, sleep and lifetime integrate with the world. Initial suspension foundation qualified against Jolt at 60/120 Hz in Debug/Release on macOS ARM64; tire traction and driving remain future work.

- `Ragdoll3D.move_to_pose` and `move_to_local_pose` drive a kinematic pose over a duration; `resume_simulation` restores dynamic members with their masses and current velocities. Rotated frames, offset centers, external contact and release are qualified against Jolt at 60/120 Hz in Debug/Release on macOS ARM64.

- Spatial motorized ragdoll: nonparallel frames, combined swing/twist targets, triangular supports and an oblique impulse qualified against Jolt at 60/120 Hz in Debug/Release on macOS ARM64. Geometry and mean reactions over established windows, center-of-mass angular balances and the global Y component; existing solver and budgets retained.

- `World3DSettings.velocity_iterations` controls contact and joint convergence from 1 to 128 iterations per stage, retaining the default of 12. A fully mobile two-motor chain against the floor uses 48 iterations to qualify anchors, limits, mean reactions and contact departure/return against Jolt at 60/120 Hz in Debug/Release. No performance gain or general impact parity is claimed.

- Free ragdoll chain with two bounded swing/twist joints: opposed oblique impulses, exercised stops and global momentum/energy balances qualified against Jolt at 60/120 Hz in Debug/Release. General contacts and impact trajectories remain open; solver and API unchanged.

- An offset ragdoll member with a fixed root combines bounded swing/twist targets, floor contact, lifting, return and passive release with an angular impulse. Geometry and window-mean equilibria are qualified against Jolt at 60/120 Hz in Debug/Release; instantaneous velocity/force equality and general impacts remain open. Solver and API unchanged.

- Two asymmetric twist stops in a passive ragdoll are qualified under opposed angular impulses against Jolt: transmission to parents, angular momentum, energy and settled states at 60/120 Hz in two world orientations in Debug/Release. No contact or solver change.

- `Ragdoll3D.drive_to_pose` and `drive_to_local_pose` track target rotations with bounded torques and no teleportation; `stop_motors` makes joints passive. Settled poses of an offset chain under gravity are compared with Jolt at 60/120 Hz in Debug/Release.

- `World3DSettings.position_iterations` configures contact and joint position correction at world creation, from 1 to 128 passes, retaining the default of 4. The ragdoll impact example uses 32 passes with anatomical limits and nonadjacent internal collisions.

- Passive three-sphere ragdoll: off-center impulse, transmission, momentum balances, anchors and symmetric floor fall qualified against Jolt at 60/120 Hz in Debug/Release; solver unchanged.

- Reusable ragdoll hierarchy: world/local poses, body and mass-center offsets, independent instances, parent/child filtering and safe lifetime; pose conventions and allowed pairs compared with Jolt ragdolls in Debug/Release.

- Adopts one `Result` declaration: an ordinary call returns the value or
  stops the program on failure; `try call()` keeps the `Result`. Existing calls
  storing results and propagating failures are made explicit. This revision
  requires the development toolchain with these `try` semantics; publication
  must coordinate compiler and package versions.

- Hinges carried by a rotating body transport cached torque into the current frame and retain consistent axes throughout the step. A gravity-loaded swing/twist shoulder and motorized elbow are qualified against Jolt at 60/120 Hz with budgets, reactions and split-phase balances.

- Simultaneous three-axis swing/twist servos under gravity: offset anchor, rotated frames, reversal and recentering, reactions and steady states qualified at 60/120 Hz against Jolt; lever timing documented without solver changes.

- Spatial hinge and vertical slider chain with an offset load: gravity, floor contact, reversal, vector reactions and budgets qualified against Jolt at 60/120 Hz, without a solver change.

- A motorized hinge chain retains an arm held by a zero velocity motor during sustained pressure against a floor: persistent support participates in the solve before integration. Efforts carry across phases without double application, teleportation invalidates the cache, and the recipe and balances are qualified against Jolt at 60/120 Hz.

- Contact followed by release in a chain with two perpendicular hinges: balances with contact impulses and application points, loads and reversal qualified at 60/120 Hz against Jolt; recipe and limits documented, solver unchanged.
- Loaded chain with two perpendicular hinges: force, spin and total angular momentum balances, reactions and reversal qualified at 60/120 Hz against Jolt; spatial recipe without contacts documented, solver unchanged.

- Dynamic rail held under gravity, with axial impact and wall release: balances, weight reactions, budgets and real contact qualified at 60/120 Hz; measured Silex and inferred Jolt impulses distinguished, planar recipe documented without a solver change.

- Qualified a dynamic hinged rail carrying a driven carriage: angular momentum, reactions and budgets checked with two masses at 60/120 Hz, with free or driven rotation; planar recipe and transient differences documented, solver unchanged.

- Fixed rails and rotation at ±0.2 rad/s: world impulse balance, motor braking and analytical free motion qualified at 60/120 Hz; application/observation frames distinguished, with Jolt transient gaps retained and no solver change.

- Rigid hinge stop impacts: impulse balance, dissipative work and stop release qualified at 60/120 Hz; anticipatory activation explained and Jolt differences retained, without a solver change.

- Rack servo qualification with two stops and reversal: explicit short angular path, static reactions and rest compared with Jolt at 60/120 Hz; transient differences retained without a solver change.

- Hinges discard stored soft-stop effort when body mutation makes that stop inactive or changes its side; moving into the free interval retains no torque from the previous stop.

- 3D hinges converge with a fixed payload outside the rotation plane under gravity; passive preparation, reactions and motor budget retained across step changes and mutations. Full-run mechanical qualification and settled Jolt comparison; initial differences retained.

- 3D path guidance: open/closed Hermite geometry, metric drives, friction, endpoints, physical orientation transport, safe mutations and explicit pinned Jolt gap witnesses.

- 3D pulley: bounded weighted length, slack or rigid cable, tackle ratios, physical anchor reactions, safe mutations and Jolt witnesses.

- 3D rack and pinion: signed rad/m ratio, tracked phase, physical torque/force, safe mutations and Jolt witnesses.

- 3D gear: signed ratio, turn tracking, physical torques and safe mutations; pinned Jolt nonunit-ratio defect preserved explicitly.

- 3D six DOF joint: free/locked/bounded translations, per-axis drives, friction and soft linear stops; angular pyramids support ranges excluding zero and nonzero locked angles.

- 3D swing/twist joint: local frames, elliptical cone/pyramid, bounded twist, separate drives and passive friction; headless qualification.

- 3D cone joint: bounded inclination, free twist, local anchors, reactions and safe runtime mutations; headless consumers and Jolt witness.

- Sliders follow a position and velocity together with `SliderMotor3D.position_and_velocity`, symmetric or signed force bounds and a physical spring; tracking, mutations, contacts and Jolt witnesses qualified.

- Soft slider stops: physical stiffness/damping, observation/mutation, signed effort and coexistence with motors/contacts.

- Slider motors accept signed force bounds in velocity and position modes, retaining symmetric forms, imposed effort, mutation/wake, real contact and Debug/Release Jolt qualification.

- `maximum_friction_force` passively brakes a slider with mutable capacity in N, separate signed effort and motor precedence; load, stopping, contacts, sleep and Debug/Release Jolt oracle qualified.

- The `SliderMotor3D.position` servo drives target travel with a physical damped spring, bounded symmetric force and targets projected onto limits; mutations, contacts and Jolt Debug/Release oracle qualified.

- The slider `SliderMotor3D` drives signed relative speed with symmetric force capacity in N, zero-speed braking, a separate motor reaction and safe runtime mutation.

- 3D sliders: local frames, free translation along X, held orientation, optional signed rigid limits, reaction measurements and safe mutations.

- Hinges follow angle and velocity together through `HingeMotor3D.position_and_velocity`, physical spring and symmetric or signed torque bounds; tracking, mutations and public consumers qualified.

- `HingeLimitSpring3D` adds soft angular stops: physical stiffness/damping, separate signed torque and safe mutation, with rigid stops retained by default. Oscillations, load, offset pivot, motors and contacts qualified against Jolt in Native Debug/Release.

- Hinge velocity and position motors accept signed torque bounds: asymmetric, one-sided or prescribed effort, with a per-step budget, mutation and guards; existing symmetric constructors remain available.

- `maximum_friction_torque` passively brakes an unpowered hinge, with mutable capacity, separate signed effort and load holding. Step budget, motor precedence, contacts, sleep and invalidation qualified; trajectories compared against Jolt in Native Debug/Release.

- `HingeMotor3D.position` controls a signed angle with explicit stiffness/damping and bounded torque, target mutation, velocity/position modes and current hard stops. Narrowing a unilateral stop corrects the pose without creating recovery velocity.

- `FixedConstraint3D` preserves a complete relative pose, captures the current assembly or aligns two local frames, measures force/torque and supports mutation, suspension and reattachment. Loaded chains, contacts, sleep and invalidation tested; equilibrium and established motion compared against Jolt on macOS ARM64 Native Debug/Release.

- `HingeMotor3D` drives a hinge at a relative speed with a maximum torque, runtime reversal, motor off and separate effort observation. Joint preparation and contact solving share the effort limit; inertia about the pivot, stops and a pendulum qualified against Jolt in Native Debug/Release.

- `HingeConstraint3D` connects two anchors around an axis with local zero-angle frames, hard stops, force/torque reactions and runtime mutations. It shares `World3D` contacts and sleep islands; pendulums and stops compared with Jolt on macOS ARM64 Native Debug/Release.

- The rotational limit of linear CCD is qualified against Jolt: pure rotation
  or parallel translation misses contact in one step and finds it with
  subdivisions in the tested cases; no exact rotational guarantee.

- `Plane3D` represents an infinite half-space on a fixed body: distance, rays,
  sweeps, convex supports, moving compounds, sensors and linear CCD. Pair
  selection does not assign an artificial finite bound to the plane.

- Height grids accept a per-vertex hole mask and an explicit diagonal choice.
  Surviving triangles remain immutable, upward facing and replaceable on a
  fixed body; sweeps, falls, CCD and events respect openings and their real rims.

- `Cylinder3D`, `TaperedCylinder3D` and `TaperedCapsule3D` add round local-Y
  solids: continuous geometry, rays and sweeps, oblique pairs, supporting caps,
  terrain contacts and translation CCD. Circular sections provide geometric
  mass, center and inertia, including cone and containing-sphere limits.
  Compounds, filters and mutations accept the new families.

- `ShapeCast3D`, `Geometry3D.shape_cast` and `World3D.shape_cast` add capsule,
  box and convex hull translation sweeps with independent initial poses,
  bilateral triangles, identities and filters. Contact witnesses use the
  geometric boundary; orientation stays fixed and the simulation solver's
  CCD contract is unchanged.

- `SphereCast3D` and `Geometry3D.sphere_cast` sweep a sphere volume against
  qualified shapes: first face/edge/vertex impact, tangency, initial overlap and
  identities. `World3D.sphere_cast` adds filters, exclusion and a safe body handle
  with snapshots. Triangle queries are bilateral and do not mutate the world.

- Compounds accept convex children, alone or mixed with primitives: volume
  center and full inertia, queries, leaf IDs, mesh supports, sensors, shape
  replacement and linear CCD. Bounds compose leaf poses before joining them
  so compensated offsets do not cause exact sweeps between distant objects.
  Native Debug/Release and Jolt mass and geometry controls on macOS ARM64.

- Convex/mesh queries reject distant faces using conservative bounds while
  retaining the exact closest witness and its identity. Strictly identical
  edge directions are stored once in the immutable hull. These two costs
  caused poor frame rates in the new Debug scene; nearly parallel directions
  and CCD remain active. Hull-face SAT projections are shared across triangles
  within each contact pass, with identical axes and tolerance. Scene measurements
  cover macOS ARM64 Native
  Debug/Release, with no per-frame bound or result on other targets.

- Convex hulls contact fixed meshes: bilateral distance and face identity,
  four support points across planar seams, distinct valley reactions and
  merged ridge reactions. Openings, sensors, filters and linear CCD respect
  the present faces and their admissible side. `ConvexMeshScene.sx` shows
  sliding, valley support and a rotating tetrahedron.

- Translation CCD rejects pairs whose swept bounds cannot intersect before
  computing their exact distance. Convex bounds follow the actual vertices,
  including shifted local origins. This removes the Debug slowdown in the
  three-triangle scene.

- A convex hull contacts a fixed triangle: bilateral face/edge/vertex
  distances, penetration depth, support manifold, bounce, sensors, queries
  and unilateral translation CCD. The volume center preserves front-side
  selection when the local origin is shifted. `ConvexTriangleScene.sx` shows
  falling, rotation and back-face crossing. Convex/mesh, seams and convex
  compound children remain to be qualified.

- Two convex hulls can collide in either order: Euclidean exterior distance,
  containment depth, up to four face contact points and edge witnesses. The
  world retains filters, sensors, events and translational CCD.
  `ConvexPairsScene.sx` shows two dynamic bodies making contact and a kinematic
  platform carrying a convex cube. Terrain pairs and convex compound children
  remain to be qualified; frictionless stacks retain shared solver limits.

- Convex hulls can be kinematic or dynamic against spheres, boxes and capsules.
  Density computes their mass, center of mass and full inertia tensor;
  impulses, mutations, sensors and linear CCD use the same commands as
  primitives. `MovingConvexScene.sx` shows falling, rotation and a moving
  platform. Convex/terrain pairs, convex compound children
  and rotational CCD remain pending.
- Hull construction identifies a face by its supporting points, avoiding a
  duplicate face after rotating and translating a parallelepiped.

- `CharacterMover3D` moves and finds support on fixed convex hulls: slopes,
  walls, steps and ceilings, sliding and bounded overlap recovery. Sensors,
  filters, removal and state changes release support. Uphill and downhill
  paths agree with Jolt; `CharacterConvexScene.sx` provides an interactive
  example. Physical characters remain under development.

- Capsules collide with fixed convex hulls: signed distances using the entire
  axial segment, solid containment, two-point face support, compound capsule
  children and linear CCD. A capsule joins the animated wedge scene. Convex
  compound children remain unsupported.

- Boxes collide with fixed convex hulls: signed distances in either order,
  up to four contact points on actual faces, compound box children and linear
  CCD. An animated box joins the wedge scene.

- 3D CCD closes the remaining gap between its search margin and the impact
  surface. An oblique convex bounce is resolved in the step that clips motion,
  without a sticking frame before the impulse.

- `ConvexHull3D(points)` adds an immutable solid hull and `Shape3D.convex`:
  signed sphere/convex distances, rays and collisions against a fixed body,
  with linear CCD, filters and sensors. Its triangulated boundary is available
  for rendering; convex compound children remain unsupported and are rejected.

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
