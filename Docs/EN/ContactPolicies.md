# Advanced filtering and pre-solve

Contact policies are disabled by default. A collider explicitly opts into
custom filtering or pre-solve, and the world receives the corresponding
function. The ordinary path therefore creates no policy snapshot.

```silex
use GFX.Physics as Physics

func traversable(pair:Physics.ContactPairSnapshot2D) bool {
    return pair.first().material.application_id.value() != 7
}

var world = Physics.World2D()
world.set_custom_filter(traversable)
world.create_collider(body, Physics.Collider2DSettings()
    ..shape = shape
    ..enable_custom_filter = true
)
```

`ColliderSnapshot2D` provides the handle, body, shape, material, filter and
sensor state. It contains no dense slot, spatial proxy or reference to an
internal manifold. Mutating the world or a handle from a policy fails
explicitly because `step` owns the world lock.

Pre-solve may retain the contact, disable it for the current step, replace its
manifold or override friction and restitution:

```silex
func one_way(input:Physics.ContactPreSolve2D) Physics.ContactDecision2D {
    if input.pair().second().body().velocity().y > 0.0 {
        return Physics.ContactDecision2D() ..enabled = false
    }
    return Physics.ContactDecision2D()
}

world.set_pre_solve(one_way)
collider.set_contact_policy_options(false, true)
```

A replacement manifold keeps one or two finite points and a unit normal.
Friction remains finite and non-negative; restitution remains between zero and
one. A decision cannot create a pair that does not exist.

`PhysicsMaterial2D` selects `friction_combine` and `restitution_combine`
independently from `average`, `geometric_mean`, `minimum`, `maximum` and
`multiply`. When the two materials disagree, the stable order `average`,
`geometric_mean`, `minimum`, `maximum`, `multiply` selects the mode. Defaults
retain geometric mean friction and maximum restitution.

Every policy runs on the thread calling `step`, in deterministic pair order,
before solver jobs. Policy code remains responsible for synchronizing its own
external effects.
