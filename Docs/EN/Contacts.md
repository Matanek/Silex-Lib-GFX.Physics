# Persistent world contacts

`World2D` tracks broad-phase pairs and geometric contacts for every public 2D
shape. Contacts are snapshots read after `step`; their cache identity, BVH
proxy, pair table, and worker scheduling remain private.

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)

for contact in contacts {
    let first = contact.first_collider()
    let second = contact.second_collider()
    let manifold = contact.manifold()
    print("$(manifold.point_count()) $(contact.normal_impulses().count())")
}
```

`write_contacts` clears and refills the caller's list. Each `Contact2D` names
the two exact colliders and their owning bodies in stable creation-identity
order. It contains the completed manifold, one normal and tangent impulse per
point, the resolved friction and restitution, and its active state. Overloads
accept a `RigidBody2D` or `Collider2D` before the output list to select only
contacts that involve that handle. `contact_count` provides the number of
touching pairs without materializing snapshots;
`candidate_pair_count` remains the broader count of active AABB candidates.

These are autonomous completed-step values, not references into the contact
cache. If a collider is destroyed after an event was copied, its geometry,
material and application id remain readable from the event's `pair()` snapshot.
The embedded handle becomes invalid, and any attempted mutation through it
fails instead of targeting a recycled collider.

Each `Collider2D.collision_filter` applies the same symmetric category, mask,
and group rules as stateless geometry queries. Rejected collider pairs never
enter the persistent contact table. The retained
`RigidBody2DSettings.collision_filter` configures the implicit compatibility
collider.

Sensors use the same filters but remain outside `contact_count`, solid
`write_contacts`, contact islands, and the impulse solver. Current overlaps are
available through `write_sensor_overlaps(output)` or
`write_sensor_overlaps(sensor, output)`. Their opt-in transitions, along with
solid contact, hit, move, and sleep events, are documented in
[`EventsAndCCD.md`](EventsAndCCD.md).

The broad phase selects the same reusable deterministic grid for dynamic worlds
at every worker count. Pair insertion, contact refresh, and snapshot ordering
therefore remain deterministic across worker counts; fixed-shape queries keep
their dynamic-tree representation.

Capsules, convex and rounded polygons, segments, one-sided chains, and secondary
colliders of compound bodies participate in broad-phase, persistent contact,
and the common Soft Step response. Chains must be fixed bodies. Retained
manifolds warm-start up to two points, while
the touched collider or chain segment supplies friction, restitution, tangent
surface speed, and rolling resistance without changing the public read surface.

When several colliders of the same two bodies meet at a corner, the world
retains one contact per exact collider pair, independently of creation order.
Solver anchors remain relative to each center of mass: oriented-shape anchors
follow body rotation, while circle anchors remain rotation-invariant. A
compound body with an offset center of mass can therefore rotate or reverse a
kinematic target without losing its floor contact.

The headless executable proofs are grouped in
[`../Tests/Consumer/Tests/Contacts.sx`](../../Tests/Consumer/Tests/Contacts.sx):

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Contacts.sx
```

They verify creation, persistence, separation and deterministic ordering
without a window, renderer, input, or visual inspection. Dynamic response and
material behavior are covered by
[`../Tests/Consumer/Tests/DynamicShapes.sx`](../../Tests/Consumer/Tests/DynamicShapes.sx).
Collider identity, resolved impulses, current sensor overlaps and stale-value
lifetime are covered by
[`../Tests/Consumer/Tests/ContactSnapshots.sx`](../../Tests/Consumer/Tests/ContactSnapshots.sx).

## Speculative contacts

A pair can produce a manifold up to a positive separation of 0.02 m. An
inclined face retains both clipped endpoints: one may exceed that margin while
the other already touches the support. The solver can
therefore slow an approach before penetration, even with CCD disabled. A begin
event marks the appearance of a manifold, which may precede geometric touching.
A hit event requires an approach speed strictly above `hit_event_threshold`
and a normal impulse actually accumulated at that point during the step. An
approach without an impulse is not a hit.

Effective contact frequency is capped at one eighth of inverse substep duration,
then doubled for a static surface. Getters retain the configured frequency.
Snapshots preserve the separation prepared at the beginning of the step,
including circle contacts.

The [speculative witness](../../Benchmarks/SpeculativeContactsOracle2D.sx) compares
1,536 samples of circle/circle, box/box, capsule/capsule, and segment/capsule:
two step durations, one or four substeps, gaps below and above the margin,
resting pairs, and the exact hit threshold. CCD is disabled to isolate the
speculative response. These cases do not prove every shape, speed, or scene.

The [geometry witness](../../Benchmarks/GeometryOracle2D.sx) also checks four
inclined predictive faces, including one partially outside its support.
