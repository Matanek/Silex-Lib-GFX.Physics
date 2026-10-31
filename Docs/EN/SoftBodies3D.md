# Simulate cloth or a deformable volume

`World3D` simulates constrained particles alongside the rigid bodies in your
scene. The CPU solver is written in Silex. A reusable definition describes the
rest shape; every `SoftBody3D` owns independent positions and velocities.

## Create and display a shape

`SoftBody3DDefinition.cloth` builds a triangulated grid with stretch, shear and
bend constraints. `cube` builds a cube containing six tetrahedra. `vertex_mass`
is each movable vertex's mass in kilograms. Manual definitions accept inverse
masses; zero fixes a vertex. Omitting the list gives every vertex a mass of 1 kg.

The manual constructor takes positions, triangle indices in groups of three,
and constraints. `SoftEdge3D` preserves distance. `SoftBend3D` preserves the
dihedral angle between two triangles whose first two indices form their shared
edge. `SoftVolume3D` preserves a tetrahedron's signed volume. `SoftTether3D`
limits the distance from a movable vertex to a fixed vertex. Zero compliance
makes a hard constraint; increasing it softens that constraint. Compliance
coefficients are not interchangeable between constraint families.

The [executable consumer](../../Tests/Consumer/Tests/SoftBodies3D.sx) shows
windowless creation and physical checks. The orbit-camera example at
`Silex-Examples/Sources/Physics3D/SoftBodiesScene.sx` uses Space for an impulse,
A for moving anchors, P to pause time and R to recreate the instances.

`SoftBodyMesh3D(body, meshes)` creates a Scene3D asset. Put `mesh()` in the
Mesh3D component and call `update(meshes)` after physics steps. It rebuilds geometry
only when positions change after the physics step, then returns `true`. Positions and
normals are recalculated in world space, so the graphical object keeps an
identity transform. Use a `double_sided` material for cloth visible from both
sides. The mesh store is borrowed during each call; use the same `Meshes` instance
as during construction. `remove(meshes)` releases the asset; the presenter does not remove it implicitly.

## Attach, guide and apply impulses

`set_fixed_position(vertex, position)` moves a vertex with zero inverse mass,
interpolating its movement across substeps. `attach(vertex, body, local_point)`
follows a rigid body's frame in the same world. This kinematic attachment is
one-way. Destroying the rigid body freezes the vertex at its last position;
`detach(vertex)` also freezes it in place.

`set_pose` accepts `SoftPose3D` world-space targets already calculated from a
skeleton pose, with a maximum deviation and an optional backstop sphere. A
zero distance guides the vertex exactly. Targets apply to distinct movable vertices.  An empty list removes pose control.
Unlisted vertices remain simulated; blending bones and weights belongs to the
animation system. A collision can move a guided vertex after its pose constraint.

`apply_impulse(vertex, impulse)` acts on a movable vertex. Settings control
vertex collision radius, damping, gravity, friction, restitution, filtering
and pressure. Pressure is the nRT coefficient: force scales with area and the
inverse of current volume. It requires a closed, outward-oriented surface.
`set_pressure` changes that coefficient during simulation.

Read positions and velocities per vertex. `positions()` and definition lists
are independent snapshots. `set_enabled(false)` suspends an instance while
retaining its state. `World3D.step(0)` changes nothing. `destroy_soft_body`
invalidates its handle; destroying the world invalidates all its instances,
even if handles or presenters remain.

## Resolution and limits

`World3DSettings.soft_body_substeps` defaults to 8 and accepts 1–128 substeps.
More substeps improve resolution at additional computational cost. Internal
constraints follow a stable order per instance. With `enable_parallelism`,
independent instances are distributed among workers; rigid contacts and impulses
are then processed in canonical order. A single cloth retains sequential internal
resolution. A few instances with substantial meshes can already occupy multiple
workers; adding many small instances is not required to enable that distribution.
Steps remain synchronous and reject world mutations during execution.

Every vertex has a collision sphere. It reacts to enabled rigid shapes allowed
by filtering; sensors produce no response. Dynamic rigid bodies receive opposite
impulses, including their inertia. A sweep protects fast vertex movement through
fixed obstacles. Rigid movement is resolved before the soft-body phase of each
step; this is not a simultaneous solve of all rigid and soft constraints.

Fixed obstacles reuse prepared geometry while their shape and pose remain
unchanged. Filters, enabled state and materials remain live body state. The
number of substeps and contact order do not change.

Triangular surfaces use a 0.1 m backing recovery layer and front-facing edges,
following Jolt’s CPU policy. Existing world queries and rigid contact lists
concern rigid bodies; the Scene3D mesh supports visual cloth selection.

The surface between vertices is not a continuous collision volume. Smaller
vertex spacing helps cover small obstacles. As in the retained Jolt reference,
self-collision and soft/soft collisions are unavailable. Rigid articulated joints,
oriented Cosserat rods, tearing and fracture are outside this API.

Invalid or degenerate topology, invalid masses/compliance, pressure on an open
surface and stale references panic, consistently with this package's other
creation contracts.
