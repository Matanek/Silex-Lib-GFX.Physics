# Persistent world contacts

`World2D` tracks broad-phase pairs and geometric contacts for every public 2D
shape. Contacts are snapshots read after `step`; their cache identity, BVH
proxy, pair table, and worker scheduling remain private.

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)

for contact in contacts {
    let first = contact.first_body()
    let second = contact.second_body()
    let manifold = contact.manifold()
    print(manifold.point_count())
}
```

`write_contacts` clears and refills the caller's list. Each `Contact2D` names
the two live body handles in stable creation-identity order and contains the
current geometric manifold. Destroying a body invalidates old handles in the
usual way and removes every pair that referenced it. `contact_count` provides
the number of touching pairs without materializing snapshots;
`candidate_pair_count` remains the broader count of active AABB candidates.

`RigidBody2DSettings.collision_filter` applies the same symmetric category,
mask, and group rules as stateless geometry queries. Rejected pairs never
enter the persistent contact table.

The broad phase selects a reusable uniform grid for mono-worker and all-circle
worlds. When explicit parallelism is enabled for non-circle shapes, a dynamic
AABB tree counts and fills newly discovered pairs through disjoint worker
ranges. Pair insertion, contact refresh, and snapshot ordering remain
deterministic across worker counts.

Capsules, convex and rounded polygons, segments, and one-sided chains now
participate in broad-phase and persistent contact generation. Chains must be
fixed bodies. In this reconstruction step their contacts are intentionally
geometric only: the legacy solver still applies impulses and positional
correction only to unrounded boxes and circles. The future Soft Step switch
will consume the retained general manifolds without changing this public read
surface.

The headless executable proof is
[`../Examples/World2D/Contacts.sx`](../Examples/World2D/Contacts.sx):

```text
silex run Packages/GFX.Physics/Examples/World2D/Contacts.sx
```

It prints one created contact, the same persisted contact on the next step,
then zero contacts after separation. It requires no window, renderer, input,
or visual inspection.
