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

Each `Collider2D.collision_filter` applies the same symmetric category, mask,
and group rules as stateless geometry queries. Rejected collider pairs never
enter the persistent contact table. The retained
`RigidBody2DSettings.collision_filter` configures the implicit compatibility
collider.

Sensor bodies use the same filters but remain outside `contact_count`,
`write_contacts`, contact islands, and the impulse solver. Their opt-in overlap
transitions, along with solid contact, hit, move, and sleep events, are
documented in [`EventsAndCCD.md`](EventsAndCCD.md).

The broad phase selects the same reusable deterministic grid for dynamic worlds
at every worker count. Pair insertion, contact refresh, and snapshot ordering
therefore remain deterministic across worker counts; fixed-shape queries keep
their dynamic-tree representation.

Capsules, convex and rounded polygons, segments, one-sided chains, and secondary
colliders of compound bodies participate in broad-phase and persistent contact
generation. Chains must be fixed bodies. Contact snapshots still identify the
two owning bodies; collider identity is a later event/contact milestone.
Contact response currently covers the primary rigid box and circle forms;
the common Soft Step solver consumes their retained manifolds without changing
this public read surface. Response for the remaining geometric forms stays an
explicit later capability rather than silently receiving partial response.

The headless executable proofs are grouped in
[`../Tests/Consumer/Tests/Contacts.sx`](../../Tests/Consumer/Tests/Contacts.sx):

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Contacts.sx
```

They verify creation, persistence, separation and deterministic ordering
without a window, renderer, input, or visual inspection.
