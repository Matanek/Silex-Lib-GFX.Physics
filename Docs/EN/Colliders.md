# Colliders and materials

`RigidBody2D` owns motion and lifetime. `Collider2D` owns collision geometry,
density, material, filter, sensor state, and contact-event options. Both are
stable typed handles; neither exposes a slot, generation, proxy, or native
pointer.

```silex
var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..create_implicit_collider = false
)

let material = Physics.PhysicsMaterial2D()
    ..friction = 0.8
    ..restitution = 0.2
    ..rolling_resistance = 0.05
    ..tangent_speed = 1.5
    ..application_id = Physics.PhysicsMaterialId2D(12)

var hull = world.create_collider(body, Physics.Collider2DSettings()
    ..shape = Physics.Shape2D.box(Physics.Box2D(Math.Vec2(2.0, 1.0)))
    ..density = 2.0
    ..material = material
)
var trigger = world.create_collider(body, Physics.Collider2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(1.0))
    ..is_sensor = true
    ..enable_sensor_events = true
)
```

A body may have zero, one, or several colliders. The default body constructor
retains source compatibility: `RigidBody2DSettings.shape`, `friction`,
`restitution`, `collision_filter`, sensor state, and event options create one
equivalent implicit collider. Set `create_implicit_collider = false` when the
body must start empty, then add explicit colliders with
`World2D.create_collider`.

`RigidBody2D.collider_count` and `write_colliders` expose the ownership
relationship. `Collider2D.body` returns the live owner. Geometry, density,
material, segment materials, filter, sensor state, and event options can be
changed through the collider handle while the world is unlocked. Topology and
broad-phase data are rebuilt before the next `step`.

`World2D.destroy_collider` invalidates that handle and removes its geometry
from the next step. Destroying a body invalidates every collider it owns. If a
body has no collider, the retained compatibility accessor `RigidBody2D.shape`
fails explicitly; it never invents public geometry.

`PhysicsMaterial2D` contains friction, restitution, rolling resistance,
tangent surface speed, and the opaque application identifier
`PhysicsMaterialId2D`. A chain uses `material` for every segment by default or
accepts exactly one `segment_materials` entry per segment. Per-segment
materials on another shape, and mismatched chain cardinality, are rejected.
Chains remain restricted to fixed bodies.

The current solver boundary remains explicit. The primary box/circle collider
keeps the established friction and restitution response. Compound and general
colliders participate in broad-phase, filtering, persistent geometric contact,
and sensor discovery, while complete response for every collider pair,
rolling resistance, and tangent speed belongs to the later response milestone.
Each collider's density now contributes to the body's composed mass, center of
mass, and inertia. Contact and sensor snapshots still identify bodies until
collider-level event identity is added.

The isolated consumer proof is
[`../Tests/Consumer/Tests/Colliders.sx`](../../Tests/Consumer/Tests/Colliders.sx).
It covers empty and compound bodies, shortcut compatibility, mutations,
filters, sensors, chain materials, collider destruction, and body-owned
invalidation.
