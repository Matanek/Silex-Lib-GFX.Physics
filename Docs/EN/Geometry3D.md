# Standalone 3D geometry

`GFX.Physics` provides spheres, boxes, capsules, cylinders and tapered shapes, convex hulls, triangles, planes, meshes, immutable compounds, and rigid poses as Silex values. They
support distance, overlap, and ray queries without a world, scene, or renderer.
The [3D world](World3D.md) uses these first shapes for free body motion.

```silex
use GFX.Physics
use STD.Math

let sphere = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
let box = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0, 1.0, 3.0)))
let capsule = Physics.Shape3D.capsule(Physics.Capsule3D(0.25, 0.5))
let pose = Physics.Transform3D(
    position:Math.Vec3(2.0, 3.0, 4.0),
    rotation:Math.Quat.angle_axis(Math.half_pi(), Math.Vec3.up())
)
let point = pose.point(Math.Vec3.right())
assert(pose.inverse_point(point).nearly_equal(Math.Vec3.right(), 0.00001))

let placed_sphere = Physics.ShapePlacement3D(sphere)
let placed_box = Physics.ShapePlacement3D(box, pose)
let gap = Physics.Geometry3D.distance(placed_sphere, placed_box)
let touching = Physics.Geometry3D.overlaps(placed_sphere, placed_box)
let hit = Physics.Geometry3D.ray_cast(
    Physics.Ray3D(Math.Vec3(-4.0, 3.0, 4.0), Math.Vec3(8.0, 0.0, 0.0)),
    placed_box
)
```

`Box3D` takes full dimensions centered on the local origin; `half_size()`
returns the half extents. `Sphere3D` takes a positive radius.
`Capsule3D(radius, half_height)` surrounds a local vertical segment of length
`2 × half_height`; its total height is `2 × (half_height + radius)`. All three shapes
reject non-finite or non-positive values. A `Transform3D` stores a finite
position and a unit quaternion. `point` and `vector` apply its rotation;
`point` also adds the translation. `inverse_point` and `inverse_vector`
undo these operations. A quaternion already close to unit length is normalized
after validation; zero, non-finite, or substantially non-unit quaternions are
rejected.

The conventions follow `STD.Math`: right-handed coordinates with Y up. A pose
has no scale; dimensions belong to the shape. Transforms do not silently fix
an invalid quaternion.

## Plane and half-space

`Plane3D(normal:Math.Vec3.up(), offset:0.0)` defines the local half-space
`normal.dot(point) <= offset`. A finite nonzero direction is normalized;
`offset` remains the signed length along that direction.
`Plane3D(Math.Vec3(0.0, 2.0, 0.0), 1.0)` therefore has its surface at `y=1`.
The pose transforms the plane without giving it a size or thickness.

```silex
use GFX.Physics
use STD.Math

func main() {
    let floor = Physics.ShapePlacement3D(Physics.Shape3D.plane(Physics.Plane3D()))
    let cast = Physics.ShapeCast3D(Physics.ShapePlacement3D(
        Physics.Shape3D.cylinder(Physics.Cylinder3D(0.5, 0.5)),
        Physics.Transform3D(Math.Vec3(10000.0, 2.0, 0.0))), Math.Vec3(0.0, -4.0, 0.0))
    let hit = Physics.Geometry3D.shape_cast(cast, floor)
    assert(hit.hit && Math.abs(hit.fraction - 0.375) < 0.00001)
}
```

`Shape3D.plane` supports distances and overlaps with convex volumes or
compounds, and is a target for rays, sphere sweeps and convex shape sweeps.
Distance uses the deepest volume support towards the half-space, its
projection on the plane, and a normal from the volume towards the plane.
A ray starting inside the occupied half-space returns `fraction=0`, its origin
as point and the outward normal; it does not search for an exit. An initially
overlapping sweep also returns fraction zero, with a point on the plane.
The plane cannot be the moving volume in ShapeCast3D.

In the world, a plane requires a fixed body; dynamic bodies, kinematic bodies,
compound children and plane/plane distances are rejected. Contacts, sensors,
filters, mutations and translation CCD visit volumes or compound leaves.
Flat caps and convex faces retain up to four supporting points; no giant
radius limits body selection. Selection visits each active plane against
enabled bodies. Floating coordinates retain their usual precision: an infinite
surface does not remove numerical limits at large coordinates.

The analytic geometry is infinite. Pinned Jolt uses a virtual broadphase box
with configurable half-extent (1000 by default) and states that contacts near
that boundary are inconsistent; this internal option is not part of the Silex
API. Jolt query controls are qualified inside that region, distant Silex
contacts independently.

## Cylinders and tapered shapes

`Cylinder3D(radius, half_height)` is a solid cylinder with flat caps, local Y
axis and height `2 × half_height`. Radius and half-height must be finite and
positive. `TaperedCylinder3D(top_radius, bottom_radius, half_height)` joins two
disks with a conical surface; one radius may be zero to form a cone.
`TaperedCapsule3D(top_radius, bottom_radius, half_height)` is the convex hull of
two spheres centered at `y=±half_height`, joined tangentially. Its radii must be
positive and its half-height may be zero. When one sphere contains the other,
the geometry becomes that offset sphere. Computed extents must also stay finite.

```silex
use GFX.Physics
use STD.Math

func main() {
    let cylinder = Physics.Shape3D.cylinder(Physics.Cylinder3D(0.5, 0.5))
    let cone = Physics.Shape3D.tapered_cylinder(Physics.TaperedCylinder3D(0.0, 0.5, 0.5))
    let capsule = Physics.Shape3D.tapered_capsule(Physics.TaperedCapsule3D(0.25, 0.5, 0.5))
    let hit = Physics.Geometry3D.shape_cast(Physics.ShapeCast3D(
        Physics.ShapePlacement3D(cylinder, Physics.Transform3D(Math.Vec3(-3.0, 0.0, 0.0))),
        Math.Vec3(6.0, 0.0, 0.0)), Physics.ShapePlacement3D(cone))
    assert(hit.hit)
    var world = Physics.World3D()
    var body = world.create_rigid_body(Physics.RigidBody3DSettings() ..shape = capsule)
    print(body.mass_properties().local_center.y)
}
```

The `Shape3D.cylinder`, `tapered_cylinder` and `tapered_capsule` variants work
with fixed, kinematic and dynamic bodies, compound children and standalone or
filtered world queries. Rays and sweeps retain the true round boundary;
collision never substitutes a faceted hull. Triangle and mesh queries are
two-sided; physical contacts follow the front-face policy. A flat cap uses up
to four constraints prepared from its support points and clipped to the surface.
Meshes retain both distinct supports in a valley and merge identical seam or
ridge reactions. Exposed spherical caps of a tapered capsule retain their
analytic edge-contact normal.

Outside separation is Euclidean; in penetration, the axis gives the estimated
minimum translation needed to separate the volumes (move `first` opposite the
normal). Sphere/axial, sphere/box and capsule/box containment follow this
convention. Support queries use a common extent for
normalization: distance convergence `10⁻⁷`, penetration `10⁻⁵`, tangency within
`10⁻⁶`. Axial sweeps use the continuous boundary, with a `10⁻⁶` margin of that extent. Qualification covers oblique pairs,
caps, joins, containment and witnesses on both boundaries; it does not establish
a guarantee for every float or extreme coordinates.

Mass, center and inertia belong to the homogeneous solid, integrated over its
circular sections. The pose retains the origin between the two caps, which may
differ from the mass center. This geometric tapered-capsule mass differs from
Jolt's box approximation. Equal cylinder, cone, equal capsule and containing
sphere limits are qualified. Out-of-range automatic mass or inertia is rejected
for dynamic bodies; fixed or kinematic bodies and explicit mass properties
remain available as for convex hulls.

## Convex hulls

`ConvexHull3D(points)` builds a closed solid from at least four finite,
non-coplanar points. `Shape3D.convex(hull)` retains this immutable hull.
Duplicate points, interior points and redundant points on a face do not create
overlapping faces. Degenerate clouds, non-finite calculations and numerically
ambiguous boundaries are rejected. Construction uses a tolerance of one millionth
of the cloud extent; use small clouds prepared at startup. The package does not
yet provide a builder for large assets.

Sphere/convex pairs support both orders, oriented poses and face, edge and
vertex contacts. From inside, separation is the negative distance to the nearest
exit plane minus the radius; the geometric normal points toward that exit.
This historical sphere/convex exception differs from box containment. The world
uses the corresponding response normal to push the sphere out. Rays clip against
the solid's half-spaces and return the exit when
the origin is inside. `triangle_count()` and `triangle(index)` expose the outward
triangulated boundary for visualization.

The box/convex pair uses the solid boundary in either order. Its exterior
separation is Euclidean; penetration measures the minimum translation along
a separating axis, including a fully contained box. Face contacts use up to
four points on the actual polygon, independently of triangulation diagonals.
A box child of a compound follows the same path.

The capsule/convex pair uses the entire axial segment. Exterior distance is
Euclidean; penetration measures the translation needed to move the segment
and its radius outside the solid. An oblique capsule crossing the hull remains
a solid collision even when both endpoints are outside. A capsule parallel
to a face uses two points clipped to the actual polygon, including when its
caps extend beyond the edges. A capsule child of a compound uses the same pair.

The convex/convex pair uses both boundaries in either order. Exterior distance
is Euclidean, including between oblique edges. During penetration or containment,
separation measures the shortest separating translation among face normals and
crossed edge axes. Face contacts retain up to four points on their actual
polygons; an edge contact uses witnesses on its supporting segments.
When minima tie, the engine chooses a deterministic axis.

Convex/triangle pairs are bilateral in standalone queries. Exterior separation
is Euclidean at faces, edges and vertices; penetration uses the shortest
separating translation among face and edge axes. The world applies the fixed
triangle's front-side policy, with up to four points covering the actual
support polygon. Sensors, world queries and translation CCD use the same pair.
A geometric volume center, independent of the local origin and explicit body
mass properties, determines the side of the plane. A shifted hull therefore
remains equivalent when its pose compensates for the shift.

Convex/mesh uses these same triangles in either order. Bilateral distance
keeps the minimum separation and its face index, retaining the first index
on ties. In the world, coplanar triangles share a support with up to four
points, while distinct valley slopes retain both reactions. Identical ridge
reactions merge. An opening with no triangles lets a narrower hull fall
through; present edges remain real supports. See [terrain contacts](World3D.md)
for the front/back policy.

A hull can be the shape of a **fixed, kinematic or dynamic** body. Its density
determines the mass, local center of mass and full inertia tensor of a
homogeneous solid; see [body commands](World3D.md#poses-mass-and-commands).
The pose still places the origin of the supplied points, which can differ
from the center of mass. The boundary remains immutable; `set_shape` replaces
the shape and recomputes a dynamic body's mass properties.

Collisions against spheres, boxes, capsules and other hulls work in both
orders, with sensors, filters and linear CCD. A kinematic hull can push a
dynamic body. A hull may also be a child of a fixed, kinematic or dynamic
compound; its local pose places the point-cloud origin independently of the
volume center.
This qualification does not cover rotational CCD.
`CharacterMover3D` is qualified on fixed hulls for movement and support;
see [the character guide](Character3D.md). The convex family remains partial.

`Silex-Examples/Sources/Physics3D/ConvexHullScene.sx` shows
two spheres, a box and a capsule falling onto a wedge built from six points, bouncing, leaving its slope and landing on
the lower tray. The scene starts and repeats automatically.

`Silex-Examples/Sources/Physics3D/MovingConvexScene.sx` shows two convex solids
falling and rotating, including an offset center of mass, and a kinematic
convex platform carrying a sphere. Space pauses, R restarts and Escape exits.

`Silex-Examples/Sources/Physics3D/ConvexPairsScene.sx` shows a rotating
tetrahedron hitting a dynamic convex base, and a kinematic convex platform
lifting a convex cube. Every physical shape in this scene is a hull;
Space, R and Escape retain the same controls.

`Silex-Examples/Sources/Physics3D/ConvexTriangleScene.sx` shows three separate
fixed triangles: a falling and rotating tetrahedron, a supported cube with
shifted local vertices, and a cube crossing the back face before landing on
the front. Space pauses, R restarts and Escape exits.

`Silex-Examples/Sources/Physics3D/ConvexMeshScene.sx` shows a shifted cube
crossing planar seams, a cube supported in a valley and a rotating tetrahedron
landing. Alternating shades reveal the triangles. Space pauses, R restarts
and Escape closes the scene.

## Query results

`Geometry3D.distance(first, second)` accepts every pair of spheres, boxes,
and capsules, as well as sphere/triangle, capsule/triangle and box/triangle
and their mesh variants, as well as sphere/convex, box/convex, capsule/convex,
convex/convex, convex/triangle and convex/mesh, in either
order, including oriented poses.
`DistanceResult3D.separation` is positive when surfaces are apart, zero at tangency, and negative in
penetration. `normal` is a unit direction from the first shape toward the
second. The two witness points lie on their respective surfaces. When several
points are equally close, their coordinates may differ without changing the
separation. During penetration or containment, the difference between the
witnesses need not encode the penetration depth; read `separation` directly.
Concentric spheres use +X as a deterministic normal.

Inside a box, sphere/box and capsule/box distances follow the signed convention:
moving the first shape opposite the normal takes it out. Capsule depth accounts
for the whole segment and its radius, including tilted axes and segments crossing
the box. Face normals and normals of edges extruded along the segment determine
the shortest exit; exterior distance retains its Euclidean minimum.
The [containment tests](../../Tests/Consumer/Tests/BoxInterior3D.sx) check witnesses,
reverse queries, common transforms and three scales.

`Geometry3D.overlaps` counts tangency as overlap. For two boxes it uses
separating axes without calculating every closest feature. A
`Ray3D(origin, translation)` describes a segment parameterized from 0 to 1;
its origin and translation must be finite, and its translation nonzero.
`Geometry3D.ray_cast` returns `hit`, the first hit `fraction`, the point, and
the target's outward normal (or the hit side's normal for a triangle). A ray
starting inside returns its first exit. A
miss returns `hit = false`.

`Triangle3D(first, second, third)` stores three finite, noncollinear local
vertices. Their winding defines the front face through `(second - first) ×
(third - first)`; `normal()` returns that unit direction. Sphere distance uses
the closest point on the face, an edge, or a vertex. Capsule distance uses the
whole axial segment: the closest witness can lie in its middle even when both
endpoints are outside the face. Penetration also accounts for the complete
segment and radius. Box distance covers faces, edges and vertices; penetration
uses the shortest separating translation across face and edge cross axes. Distance and overlap are
geometric on both sides. A simple ray hits either face and reports a normal
opposing its direction. World contact is one-sided, as described in
[World3D](World3D.md). Other triangle pairs and triangle compounds are not
supported.

`TriangleMesh3D([triangle, ...])` copies a nonempty list of `Triangle3D`
values. Each triangle's zero-based index remains its identity until the mesh
is replaced. `triangle_count()` and `triangle(index)` expose the list. Sphere,
capsule, box and convex hull distance selects the smallest separation and keeps the first index
on a tie.
The result reports that index as `second_child_id` or `first_child_id` according
to shape order; a ray reports it as `child_id`. Standalone distance, overlap,
and ray queries remain geometric on both sides. Other mesh pairs are not
supported.

Represent a hole by omitting its triangles. On a fixed planar terrain,
a box, sphere or capsule narrower than the opening falls freely, without
support on missing faces. A wider box can rest on the existing faces around
the hole; its manifold points stay on those faces. Leaving an outer edge
ends contact and lets the body fall. These cases are qualified at 120 Hz
on a square opening, including reversed triangle order and a shared rotation
around Y. Holes in terrain with arbitrary relief remain to be qualified. Linear CCD against
fixed terrain is described in [World3D](World3D.md).

`TriangleMesh3D.from_height_grid(columns, rows, heights, column_spacing,
row_spacing, holes:[], diagonal:HeightGridDiagonal3D.column_to_row)` builds a
fixed mesh from a regular grid. `heights` is laid out by Z rows, then X columns:
sample `(column, row)` lies at
`(column × column_spacing, height, row × row_spacing)` in local coordinates.
At least two samples per axis, exactly `columns × rows` finite heights, and
positive finite spacing independently on X and Z are required.

The optional `holes` mask has one bool per sample: `true` removes triangles
using that vertex. The other triangle in a cell may survive. The mask must be
empty or have as many elements as `heights`; at least one triangle must remain.
Masked heights must also be finite. Without holes, cells generate two upward
triangles in row then column order, with IDs
`2 × (row × (columns - 1) + column)` and the next ID. With holes, IDs enumerate
the surviving faces in that order.

The default diagonal joins the next-column vertex to the next-row vertex.
`HeightGridDiagonal3D.first_to_opposite` joins the first vertex to the opposite
vertex, as in the pinned Jolt heightfield. This choice changes interpolation
in a nonplanar cell and which triangles a hole removes.

```silex
use GFX.Physics
use STD.Math

func main() {
    var grid = Physics.TriangleMesh3D.from_height_grid(2, 2,
        [0.0, 0.0, 0.0, 0.0], 1.25, 2.0,
        holes:[true, false, false, false])
    assert(grid.triangle_count() == 1)
    var world = Physics.World3D()
    var floor = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..shape = Physics.Shape3D.mesh(grid))
    floor.set_shape(Physics.Shape3D.mesh(Physics.TriangleMesh3D.from_height_grid(
        2, 2, [0.0, 0.0, 0.0, 0.0], 1.25, 2.0)))
}
```

Triangles own immutable geometry: changing the source arrays does not change
the terrain. Rebuild and call `set_shape` to replace the mesh and end contacts
from its previous revision. The mesh remains fixed, exact and uncompressed;
quantized height updates and dynamic terrains are not provided. Use
[HeightField3D](HeightField3D.md) to edit height or hole regions. A fully masked
grid is rejected; remove the body from the world to remove the entire terrain.
Ordinary meshes visit faces; grids can select nearby cells, without a
constant-cost guarantee for every query.

Separated box pairs compare vertices against faces and edges against edges.
Capsules use their axial segment; ray queries also test their hemispheres.
The queries retain no cache; the world selects candidate pairs before these
narrow queries. Convex volume sweeps and
[world queries](World3D.md#query-bodies-in-the-world) are available.

## Sweep a sphere

To stop a spherical probe before an obstacle, query its volume:

```silex
use GFX.Physics
use STD.Math

func main() {
    let obstacle = Physics.ShapePlacement3D(Physics.Shape3D.box(
        Physics.Box3D(Math.Vec3(1.0))))
    let cast = Physics.SphereCast3D(Physics.Sphere3D(0.5),
        Math.Vec3(-3.0, 0.0, 0.8), Math.Vec3(6.0, 0.0, 0.0))
    let hit = Physics.Geometry3D.sphere_cast(cast, obstacle)
    assert(hit.hit)
    print(hit.fraction) // 0.35: the volume touches the edge; its center ray misses.
}
```

`SphereCast3D(sphere, origin, translation)` describes a translated sphere,
with finite origin, endpoint and translation, nonzero translation and finite
positive radius. `Geometry3D.sphere_cast(cast, target)` returns the first impact
in `CastResult3D`: `hit`, `fraction` from 0 to 1, `point` on the target,
unit `normal` pointing out of the target toward the sphere, and `child_id`.
The center at impact is `origin + translation × fraction`. A miss returns
`hit = false`; the other fields then have no physical meaning.

The target may be a sphere, box, capsule, convex hull, triangle, mesh or
qualified compound. Faces, edges and vertices are included, as are tangency
and the segment endpoint. Triangles are bilateral, with the normal of the
hit side. The mesh face index or compound child ID is returned; a simple
shape returns `-1`. An exactly equal fraction retains the first child in
construction order.

An initial overlap or tangency returns **fraction zero**, even when moving
outward. The point comes from the distance query; a center inside a box or
convex hull uses its nearest exit face normal. Concentric configurations and
equally close faces have a deterministic witness, without a guarantee of
complete physical recovery.

The target remains stationary throughout the query. There is no rotation
sweep or implicit body movement. For other convex volumes, see
[their sweep](#sweep-a-capsule-box-or-convex-hull). Meshes and
convex hulls traverse their boundary per query; this API does not qualify very
large terrains. Numerical witnesses cover scales 0.1, 1 and 10 with rigid
poses and compensated vertex offsets; they do not bound every possible float
coordinate. To filter bodies in a world, see [World3D](World3D.md#query-bodies-in-the-world).

## Sweep a capsule, box or convex hull

To move a volume up to its first obstacle, describe its initial placement and
translation with `ShapeCast3D(placement, translation)`:

```silex
use GFX.Physics
use STD.Math

func main() {
    let obstacle = Physics.ShapePlacement3D(Physics.Shape3D.box(Physics.Box3D()))
    let probe = Physics.ShapePlacement3D(Physics.Shape3D.capsule(
        Physics.Capsule3D(0.5, 0.5)), Physics.Transform3D(Math.Vec3(-3.0, 0.0, 0.8)))
    let cast = Physics.ShapeCast3D(probe, Math.Vec3(6.0, 0.0, 0.0))
    let hit = Physics.Geometry3D.shape_cast(cast, obstacle)
    assert(hit.hit)
    print(hit.fraction) // 0.35
}
```

`Geometry3D.shape_cast(cast, target)` returns `CastResult3D`, using the sphere
sweep's fields and conventions. The impact pose keeps
`placement.transform().rotation`; its position is
`placement.transform().position + translation × fraction`. Translation must
be finite, nonzero, have finite squared length, and keep a finite endpoint.
The moving volume may be a sphere, capsule, box, cylinder, tapered cylinder, tapered capsule or convex hull; the constructor
rejects moving triangles, meshes and compounds.

All current target families are accepted, including bilateral triangles,
meshes and compounds. The first obstacle and its `child_id` are retained;
strict ties preserve construction order. Initial overlap or tangency returns
fraction zero, even when moving outward. The initial distance witness is
deterministic; it does not provide complete recovery from deep penetration.
Several contact points or normals may be geometrically valid; uniqueness is
not guaranteed.

The target and the moving volume's orientation remain fixed. Spheres reuse
analytic sweeps; other pairs advance by separating planes or distances, with
a convergence margin of `10⁻⁷` times the moving volume's extent. Rounded
tangencies may therefore be reported slightly before exact contact.
Qualification covers fractions within `0.0002`, normals within `0.002`, scales
0.1/1/10, independent poses, compensated offsets and 2,000-unit translations.
It does not bound all float values or very large terrains. Queries traverse
target leaves and do not modify bodies. See
[filtered world queries](World3D.md#query-bodies-in-the-world).

## Immutable compound

`Compound3D` takes a nonempty array of `CompoundChild3D(id, shape,
transform)`. Each child has a unique nonnegative integer ID and a local pose.
Children may be spheres, boxes, capsules, cylinders, tapered shapes or convex hulls; triangles, meshes
and nested compounds are rejected.
The constructor copies the child list, which cannot be changed afterward.
The effective pose applies the child pose, then the compound pose.

```silex
use GFX.Physics
use STD.Math

var compound = Physics.Compound3D([
    Physics.CompoundChild3D(22,
        Physics.Shape3D.sphere(Physics.Sphere3D(0.5)),
        Physics.Transform3D(position:Math.Vec3(2.0, 0.0, 0.0)))
])
let target = Physics.ShapePlacement3D(
    Physics.Shape3D.compound(compound)
)
let probe = Physics.ShapePlacement3D(
    Physics.Shape3D.sphere(Physics.Sphere3D(0.5)),
    Physics.Transform3D(position:Math.Vec3(4.0, 0.0, 0.0))
)
let result = Physics.Geometry3D.distance(probe, target)
assert(result.second_child_id == 22)
```

Distance and overlap visit the children and select the smallest signed
separation. `first_child_id` and `second_child_id` identify the selected
children, or are `-1` for a primitive. For rays, `child_id` identifies the
first child hit, or is `-1` for a miss or primitive target. Ties keep the
first child in the supplied order. Both operands of a standalone query may
be compounds. See the [3D world](World3D.md) for body support.
