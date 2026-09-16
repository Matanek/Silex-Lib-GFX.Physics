# Geometry and collision queries

`Physics.Geometry2D` provides AABBs, point tests and closest points, distance,
overlap, manifolds, ray casts and shape casts over transformed, filtered
`ShapePlacement2D` values.

```silex
use GFX.Physics
use STD.Math

let player = Physics.ShapePlacement2D(
    Physics.Shape2D.capsule(Physics.Capsule2D(
        Math.Vec2(0.0, -0.5),
        Math.Vec2(0.0, 0.5),
        0.25
    )),
    Physics.Transform2D(position:Math.Vec2(2.0, 3.0))
)
let wall = Physics.ShapePlacement2D(
    Physics.Shape2D.box(Physics.Box2D(Math.Vec2(1.0, 4.0), 0.1))
)

let distance = Physics.Geometry2D.distance(player, wall)
let contains = Physics.Geometry2D.test_point(player, Math.Vec2(2.0, 3.0))
let closest = Physics.Geometry2D.closest_point(wall, Math.Vec2(4.0, 0.0))
let manifold = Physics.Geometry2D.manifold(player, wall)
let hit = Physics.Geometry2D.shape_cast(
    player,
    Math.Vec2(-4.0, 0.0),
    wall
)
```

Dimensions and radii must be finite; circle and capsule radii must be positive,
and endpoints must be distinct. A polygon accepts three to eight points,
welds nearby points, builds their counter-clockwise convex hull, and rejects
a collinear result. A chain requires four points, and its solid side lies to
the right of its path. In an open chain, the first and final segments provide
ghost geometry for endpoint normals: only the segments between them collide.
Supply a ghost point before and after the intended collision path.

Filters use 64-bit categories and masks. Equal positive groups force contact;
equal negative groups prevent it. Distance remains purely geometric; other
queries apply filters.

Each call owns its scratch storage and can run concurrently with other calls.
The algorithms are native Silex adaptations of Box2D 3.1.1 hull, GJK, manifold
and cast algorithms. Box2D is used only as a differential oracle.

## Valid values and degenerate motion

Positions, translations and angles must be finite. `Transform2D` represents
rotation by an angle in radians: consumers do not supply a cosine/sine pair
to normalize. `AABB2D(center, half_size)` accepts zero half extents, rejects
negative components, and verifies that the resulting bounds remain finite.
Its center/half-size accessors avoid intermediate overflow when the bounds
are representable.

`Ray2D` accepts zero or very short translation. Its maximum fraction must be
finite and in `[0, 100000)`. A zero fraction is valid. The queried segment
runs from `origin` to `origin + translation * max_fraction`.
`Geometry2D.shape_cast` and corresponding world queries also accept zero
motion and a finite, non-negative maximum fraction.

A valid ray does not guarantee a hit. Starting strictly inside a circle or
capsule returns a hit at fraction zero, at the ray origin, with a zero normal.
An unrounded polygon also accepts its boundaries at fraction zero. For a
circle or capsule, a zero ray exactly on the boundary misses; an entering ray
can return a surface normal there. A ray parallel to a segment misses it.
Chains retain their solid side. Rounded polygons use a shape cast with its
contact tolerance.

An initially overlapping shape cast returns a zero fraction and normal, with
a common point between the shape witnesses. `can_encroach` allows advancement
from some shallow overlaps; it does not discard deep initial hits. A zero
normal therefore signals initial overlap without a determined entry
direction: do not use it as a unit surface normal. When `hit` is `false`, the
other fields are neutral and do not describe a contact.

Planes from `CharacterMover2D` are collision results:
`CharacterCollisionPlane2D` exposes a normalized normal, a point and a
separation for reading. There is no public general-plane constructor.
The package validates values at constructor and operation boundaries; it does
not duplicate Box2D's six boolean validation helpers. Invalid arguments
produce an immediate diagnostic.

`GeometryValuesOracle2D.sx` is paired with
`Oracle2D/GeometryValuesOracle.c`: 360 ray and shape-cast results covering
zero translation, zero fraction, small translation, boundaries, initial
overlaps, capsule caps and shifted shapes. The comparator requires exact hit
flags and compares fractions, points and normals with absolute tolerance
`2e-5` and relative tolerance `2e-6`; initial-overlap zeros are exact.
`GeometricValidityOracle.c` and `check-geometric-values.py` distinguish raw
Box2D representations from public Silex inputs. Consumer tests also verify
rotations, produced planes and world queries.

## Provenance

The adaptations originate primarily from `src/hull.c`, `src/distance.c`,
`src/geometry.c` and `src/manifold.c` at commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`. Erin Catto's copyright notices
and the MIT license are retained in `Box2D-NOTICE.txt` at the package root.
No Box2D binary enters the production runtime.
