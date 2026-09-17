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
retained aliases. When the last reachable reference to the world disappears,
the simulation ends and all its handles become invalid: bodies, colliders,
chains, and all eight joint families. `is_valid()` then returns `false`;
reading or modifying the object through that handle fails with a diagnostic.
Retaining a handle alone does not extend the simulation's lifetime. Retaining
a world alias, including one in a scene, does.

A bound scene callback can form a cycle with the world. Silex also finalizes
that cycle once it becomes unreachable. If a callback removes the last external
reference during `step` or `refresh_contacts`, the world stays alive until the
active call returns. The restrictions on mutation during a step still apply.

Contact and event snapshot data remain readable after the world ends; their
embedded handles become invalid. Creating another world never reactivates an
old handle. The pinned Box2D 3.1.1 witness differs on this last point: its raw
IDs can become valid again after a world slot is reused. Silex preserves the
original world's identity and rejects access to the new simulation.

The [lifetime tests](../../Tests/Consumer/Tests/WorldLifetime.sx) check aliases,
cycles, active callbacks, snapshots, and independent worlds.
[Stale accesses](../../Tests/Consumer/check-world-lifetime.py) are checked for
every handle family.

Explicit composition is the accepted adaptation of `b2Body_GetWorld`,
`b2Shape_GetWorld`, `b2Chain_GetWorld`, and `b2Joint_GetWorld`.
