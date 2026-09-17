# Retain the world for global operations

A handle operates on its own object: body position or impulses, collider
materials, or joint targets. To create another object, perform a spatial query,
or destroy an object, retain the relevant `World2D` in your scene or pass it
explicitly to the function.

```silex
func spawn_neighbor(world:Physics.World2D, body:Physics.RigidBody2D) Physics.RigidBody2D {
    return world.create_rigid_body(Physics.RigidBody2DSettings()
        ..position = body.position().add(Math.Vec2(2.0, 0.0)))
}
```

The same rule applies to bodies, ordinary and chain colliders, and all eight
joint families. `collider.body()` and joint body accessors recover the connected
bodies; they do not recover the world. No handle currently exposes `world()`.

`World2D` is a shared class: retaining it in a scene object keeps the same
simulation accessible without copying its state. The
[consumer tests](../../Tests/Consumer/Tests/WorldOwnership.sx) exercise creation,
queries, collider replacement, body replacement through each of the eight
joint families, and invalidation of explicitly destroyed handles.

Explicit body destruction invalidates its colliders and joints, including
retained aliases. Letting only the world variable leave scope currently does
**not** establish global invalidation: a retained handle can still access its
storage. World lifetime remains under qualification; retain the world while
using its objects.

Explicit composition is the accepted adaptation of `b2Body_GetWorld`,
`b2Shape_GetWorld`, `b2Chain_GetWorld`, and `b2Joint_GetWorld`. It does not
resolve the separate obligation to qualify global world lifetime.
