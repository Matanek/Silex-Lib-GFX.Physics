# Filter joints and existing contacts

An active `FilterJoint2D` prevents collision between its two bodies. Create it
to suspend their contacts, then destroy it to allow collision again:

```silex
let filter = world.create_filter_joint(first, second)
world.step(1.0 / 60.0)
// Contacts between first and second have been removed.
world.destroy_joint(filter)
world.step(1.0 / 60.0)
// Contacts are rediscovered if the shapes are close and other filters allow them.
```

Creation also applies to existing contacts: they no longer produce a physical
response on the next step, and enabled end events are published. Destruction
requests contact discovery without requiring body movement. Another blocking
joint or collider filter can still prevent contacts from returning.

A filter joint has no `set_collide_connected` switch: its presence expresses
the prohibition. Destroying it invalidates its handle. Mechanical joints retain
`set_collide_connected` because they can constrain bodies while allowing them
to collide.

## Difference from Box2D 3.1.1

The raw reference retains existing contacts when `b2CreateFilterJoint` is
called. They may continue slowing bodies despite the new joint. Destruction
alone does not request immediate rediscovery of a stationary pair either.
Physics applies the new policy on the next step in both cases.

The C witness preserves those raw results. Its `--immediate` mode uses only
the reference public API to express the same usage: call
`b2Joint_SetCollideConnected(true)` then `false` just after filter joint creation,
and `true` just before destroying a blocking joint. It does not modify the
reference or claim that the raw call sequences are equivalent.

The [Silex witness](../../Benchmarks/FilterJointOracle2D.sx) compares 24 stages:
creation before/after contact, separation, reentry, destruction, mutation and
repeated configuration of a motor joint with no force. Two surfaces preserve
their identities in contacts and events. Position, velocity and impulse also
check the physical consequence. The comparator requires all nine divergent
raw-reference stages to remain explicitly identified.
