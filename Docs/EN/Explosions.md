# Explosions and radial impulses

`World2D.explode` applies a radial impulse in one call to dynamic bodies with
at least one eligible collider inside the radius.

```silex
var affected:Physics.ExplosionResult2D[] = []
world.explode(Physics.Explosion2DSettings()
    ..center = Math.Vec2(4.0, 2.0)
    ..radius = 6.0
    ..impulse = 12.0
    ..falloff = Physics.ExplosionFalloff2D.quadratic,
    affected
)

for result in affected {
    print(result.body().debug_label())
    print(result.impulse)
}
```

Falloff is `linear` by default; `constant` and `quadratic` cover the other
common intents. The settings' `QueryFilter2D` is distinct from contact
filtering. Fixed, kinematic, disabled bodies and rejected colliders receive no
impulse. `wake = false` also leaves a sleeping body untouched.

A compound body receives one impulse. Its magnitude is capped by its strongest
collider contribution, while its application point is the weighted average of
eligible surface points. The result can therefore produce torque without
artificially multiplying the maximum impulse.

The buffer-free overload, `world.explode(settings)`, returns only the number of
affected bodies. The center and scalar values must be finite, the radius must
be positive, and the impulse must be non-negative. Explosions add no damage,
particle, or audio gameplay rules.
