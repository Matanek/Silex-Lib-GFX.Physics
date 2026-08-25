# Active islands and sleep

`World2D` groups touching dynamic bodies into deterministic internal islands.
The island graph is an implementation detail: consumers observe transitions
through `RigidBody2D.is_awake()` and the aggregate `World2D.awake_body_count()`.
No union-find root, dense body index, contact slot, or future solver color is a
public identity.

```silex
world.step(1.0 / 60.0)
print(body.is_awake())
print(world.awake_body_count())
```

At the beginning of a step, awake dynamic bodies are gathered in stable body
identity order into one reusable contiguous list. Serial integration walks only
that list. Parallel integration partitions the same list into disjoint ranges;
sleeping bodies therefore leave the motion hot path without changing logical
order between worker counts.

After contact generation, a reusable union-find connects touching awake bodies.
Its root is always the lowest stable body identity in the component. Bodies are
then packed by island into contiguous ranges, also in stable identity order.
The retained general-shape contacts and the historical box/circle constraints
feed the same activation graph even though dynamic response for general shapes
still waits for the Soft Step solver.

An island sleeps atomically after its linear and angular surface motion remains
below the documented thresholds. A body with sleep disabled stays awake but
does not prevent an unrelated island from sleeping. A meaningful impact wakes
only the directly touched sleeping body from one immutable awake-state
snapshot. A short cooldown prevents that wake from cascading through an entire
resting chain in the same settling interval.

Creating or destroying an unrelated body does not wake existing sleepers.
Destroying a member invalidates and rebuilds private derived storage while
preserving the awake state of surviving handles.

The headless executable proof is
[`../Examples/World2D/SleepIslands.sx`](../Examples/World2D/SleepIslands.sx):

```text
silex run Packages/GFX.Physics/Examples/World2D/SleepIslands.sx
```

It prints the active count at creation, after atomic sleep, after a staged
impact, and after deletion. It needs no renderer or visual inspection.
