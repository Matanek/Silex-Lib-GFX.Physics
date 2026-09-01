# Geometry and collision queries

`GFX.Physics` exposes a stateless 2D geometry layer independently from
`World2D`. It covers boxes with an optional rounded radius, circles, capsules,
convex polygons with up to eight input points, segments, and open or closed
chains.

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

`aabb` returns exact transformed bounds, `test_point` checks containment, and
`closest_point` projects a finite point onto the nearest surface. `distance`
returns the closest surface points, the normal from the first shape
to the second, and a non-negative separation. `overlaps` applies both placement
filters and reports whether that separation is zero. `manifold` additionally
returns a normal and up to two geometric contact points. These points have no
persistent identity or accumulated impulse in this reconstruction step.

`ray_cast` and `shape_cast` return the earliest hit within `max_fraction`.
Initial overlap is normally reported at fraction zero. On a shape cast,
`can_encroach` may continue from a shallow initial separation while still
rejecting deep initial overlap. A failed cast has `hit == false`; its other
fields are neutral values and must not be interpreted as a contact.

All operations are pure read queries over value-like placements. They do not
touch a world, keep a cache, or share scratch memory, so independent calls can
run concurrently outside `World2D.step`.

## Validity and winding

Invalid public geometry fails immediately with a diagnostic:

- dimensions and radii must be finite, with positive circle and capsule radii;
- capsule and segment endpoints must be distinct;
- a polygon accepts three to eight finite input points, welds points nearer
  than the geometry tolerance, builds their convex hull, and rejects a
  collinear result;
- a rounded box or polygon radius must fit inside its convex core;
- a chain needs at least four points and rejects consecutive duplicates;
- rays need finite, non-zero translation and positive `max_fraction`.

Polygon input order is intentionally irrelevant because `Polygon2D` computes a
counter-clockwise convex hull. Chain order is meaningful: as in Box2D 3, the
solid front is the right side while looking from one point to the next. Open
chains use their first and final segments as ghost geometry for endpoint
normals; only the segments between those ghosts collide. Supply one ghost point
before and after the intended collision path. Looped chains instead close the
last point to the first implicitly, so callers must not repeat the first point.

`CollisionFilter2D` uses 64-bit category and mask bits. Both masks must accept
the other category. Equal non-zero positive group indices force a match, while
equal negative indices reject one. Distance is a purely geometric measurement
and therefore does not apply collision filters; overlap, manifold, ray, and
shape casts do.

## Origin and verification

The convex-hull, GJK distance, conservative advancement, manifold, and cast
designs are native Silex adaptations of the public collision geometry in
Box2D `v3.1.1`, commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`, principally `src/hull.c`,
`src/distance.c`, `src/geometry.c`, and `src/manifold.c`. Box2D is Copyright
(c) 2022 Erin Catto and distributed under the MIT License. Its code is neither
linked into nor shipped by this package; the pinned build is only a
differential benchmark oracle.

The Release witness compares transformed distance, capsule-circle manifold,
polygon ray cast, fast shape cast, convex and degenerate hulls, and both sides
of a one-sided chain segment. Consumer tests add rounded shapes, two-point face
manifolds, filter groups, coincident centers, crossing segments, invalid public
inputs, transformations, and parallel read queries.

The GJK simplex deliberately stores mutable vertices in reference-backed
private objects. Mutable structs reached through a collection currently lose
some nested writes in the Silex Release backend even though Debug preserves
them. This internal workaround can be removed when that compiler discrepancy
is fixed; no reference identity leaks into the public geometry API.

`World2D` attaches every public shape and retains their geometric contacts.
Its existing regression solver still applies dynamic response only to
unrounded boxes and circles; see [`Contacts.md`](Contacts.md) for that boundary.
