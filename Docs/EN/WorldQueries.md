# World spatial queries

`World2D` queries its living colliders directly without exposing proxy ids or
spatial-acceleration traversal order. `write_*` variants replace a caller-owned
buffer and return traversal statistics. `*_any` variants answer at the first
logical hit, while `*_closest` variants retain the smallest fraction.

```silex
var overlaps:Physics.Collider2D[] = []
let stats = world.write_aabb_overlaps(
    Physics.AABB2D(Math.Vec2(4.0, 2.0), Math.Vec2(1.0)),
    overlaps,
    Physics.QueryFilter2D(mask_bits:0x4)
)

var casts:Physics.WorldCastResult2D[] = []
world.write_ray_casts(
    Physics.Ray2D(Math.Vec2(), Math.Vec2(10.0, 0.0)),
    casts
)
var closest = world.ray_cast_closest(
    Physics.Ray2D(Math.Vec2(), Math.Vec2(10.0, 0.0))
)
```

Overlap queries accept either an `AABB2D` or a `ShapePlacement2D`. Shape casts
add a translation and maximum fraction. Every `all` result follows collider
creation identity regardless of position, internal compaction, or worker
count. `WorldCastResult2D` exposes point, normal, and fraction; `collider()` is
valid only when `hit` is true.

`QueryFilter2D` is distinct from `CollisionFilter2D`. Its category and mask
select collider categories without creating or modifying a contact pair.
Disabled bodies are absent from queries.

A `Collider2D` provides `test_point`, `ray_cast_local`, `world_aabb`,
`closest_point`, and mass properties for its own geometry.
`RigidBody2D.world_aabb()` combines all its collider bounds. Handles retained
in a result become invalid when their collider is destroyed.

Queries are rejected during `step`. Multiple readers may share a resting
world: each call owns its temporary values and the consumer owns its output
buffer. `WorldQueryStatistics2D` reports visited colliders, AABB candidates,
and hits without exposing storage details.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/WorldQueries.sx
```

The pinned Box2D 3.1.1 witness covers AABB, shape overlap, ray cast, shape cast,
and local collider queries. Silex reports exact geometry bounds; Box2D adds a
2 cm broad-phase margin in `b2Shape_GetAABB`, which the checker records as an
explicit tolerance.
