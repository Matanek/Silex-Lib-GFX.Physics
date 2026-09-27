# First 3D geometry values

`GFX.Physics` provides spheres, boxes, and rigid poses as Silex values. They
can be created without a world, scene, or renderer. The 3D physics world and
queries between shapes are not available yet.

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
```

`Box3D` takes full dimensions centered on the local origin; `half_size()`
returns the half extents. `Sphere3D` takes a positive radius. Both shapes
reject non-finite or non-positive values. A `Transform3D` stores a finite
position and a unit quaternion. `point` and `vector` apply its rotation;
`point` also adds the translation. `inverse_point` and `inverse_vector`
undo these operations.

The conventions follow `STD.Math`: right-handed coordinates with Y up. A pose
has no scale; dimensions belong to the shape. Transforms do not silently fix
an invalid quaternion.
