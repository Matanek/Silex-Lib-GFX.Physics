# Standalone 3D geometry

`GFX.Physics` provides spheres, boxes, capsules, triangles, immutable compounds, and rigid poses as Silex values. They
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
exit plane minus the radius; the geometric normal points toward that exit, as
for sphere/box. The world uses the corresponding response normal to push the
sphere out. Rays clip against the solid's half-spaces and return the exit when
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
around Y. Holes on sloped terrain remain to be qualified. Linear CCD against
fixed terrain is described in [World3D](World3D.md).

`TriangleMesh3D.from_height_grid(columns, rows, heights, column_spacing,
row_spacing)` builds a fixed mesh from a regular grid. `heights` is laid out
by Z rows, then X columns: sample `(column, row)` lies at
`(column × column_spacing, height, row × row_spacing)` in local coordinates.
At least two samples per axis, exactly `columns × rows` finite heights, and
positive finite spacing on both axes are required. Each cell generates two
upward-facing triangles, ordered by row and then column. Their IDs are
`2 × (row × (columns - 1) + column)` and the next ID. The resulting triangle
list is immutable and can be used as `Shape3D.mesh(grid)` on a fixed body.
Existing queries still walk individual triangles; this API does not claim
large-terrain query performance. Holes and mutable heights are not supported.

Separated box pairs compare vertices against faces and edges against edges.
Capsules use their axial segment; ray queries also test their hemispheres.
The queries retain no cache; the world selects candidate pairs before these
narrow queries. Sweeps of other volumes remain to be delivered;
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
sweep, implicit body movement, or public box/capsule/convex sweep. Meshes and
convex hulls traverse their boundary per query; this API does not qualify very
large terrains. Numerical witnesses cover scales 0.1, 1 and 10 with rigid
poses and compensated vertex offsets; they do not bound every possible float
coordinate. To filter bodies in a world, see [World3D](World3D.md#query-bodies-in-the-world).

## Immutable compound

`Compound3D` takes a nonempty array of `CompoundChild3D(id, shape,
transform)`. Each child has a unique nonnegative integer ID and a local pose.
Children may be spheres, boxes, capsules or convex hulls; triangles, meshes
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
