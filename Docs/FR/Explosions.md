# Explosions et impulsions radiales

`World2D.explode` applique en un appel une impulsion radiale aux corps
dynamiques dont au moins un collider admissible se trouve dans le rayon.

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

L’atténuation est `linear` par défaut ; `constant` et `quadratic` couvrent les
autres intentions usuelles. Le `QueryFilter2D` des réglages est distinct du
filtre de contacts. Les corps fixes, cinématiques, désactivés et les colliders
rejetés ne reçoivent rien. `wake = false` laisse également un corps endormi
intact.

Un corps composé ne reçoit qu’une impulsion. Sa magnitude est plafonnée par la
contribution la plus forte de ses colliders, tandis que son point d’application
est la moyenne pondérée des points de surface admissibles. Le résultat reste
donc sensible au couple sans multiplier artificiellement l’impulsion maximale.

La surcharge sans buffer, `world.explode(settings)`, retourne seulement le
nombre de corps affectés. Centre et valeurs doivent être finis, le rayon doit
être strictement positif et l’impulsion non négative. Les explosions
n’introduisent aucune règle de dégâts, particule ou audio.
