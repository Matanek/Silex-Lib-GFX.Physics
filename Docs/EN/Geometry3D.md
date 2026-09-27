# Standalone 3D convex geometry

`GFX.Physics` provides spheres, boxes, and rigid poses as Silex values. They
support distance, overlap, and ray queries without a world, scene, or renderer.
The [3D world](World3D.md) uses these first shapes for free body motion.

```silex
use GFX.Physics
use STD.Math

let sphere = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
let box = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0, 1.0, 3.0)))
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
returns the half extents. `Sphere3D` takes a positive radius. Both shapes
reject non-finite or non-positive values. A `Transform3D` stores a finite
position and a unit quaternion. `point` and `vector` apply its rotation;
`point` also adds the translation. `inverse_point` and `inverse_vector`
undo these operations. A quaternion already close to unit length is normalized
after validation; zero, non-finite, or substantially non-unit quaternions are
rejected.

The conventions follow `STD.Math`: right-handed coordinates with Y up. A pose
has no scale; dimensions belong to the shape. Transforms do not silently fix
an invalid quaternion.

## Query results

`Geometry3D.distance(first, second)` accepts every pair of the available
spheres and boxes, including oriented boxes. `DistanceResult3D.separation` is
positive when surfaces are apart, zero at tangency, and negative in
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
the target's outward normal. A ray starting inside returns its first exit. A
miss returns `hit = false`.

Separated box pairs compare vertices against faces and edges against edges.
The query retains no cache; future world collision detection will select
candidate pairs before calling these narrow queries. Other shape families,
shape casts, and world queries remain to be delivered.
