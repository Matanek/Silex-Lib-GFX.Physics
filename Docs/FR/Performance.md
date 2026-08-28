# Contrat de performance de World2D

La performance est un contrat mesuré, jamais une déduction à partir du nombre
de corps. Les benchmarks séparent mouvement clairsemé, contacts denses,
sommeil, joints, workers et coût du rendu.

## Exécuter le corpus

```text
silex run Packages/GFX.Physics/Benchmarks/World2D.sx --release
silex run Silex-Benchmarks/Sources/PhysicsWorldScale2D.sx --release
silex compile Packages/GFX.Physics/Benchmarks/CircleScale2D.sx --release -o /tmp/gfx-circle-scale
/tmp/gfx-circle-scale --count-5000 --long --awake
/tmp/gfx-circle-scale --count-1800 --falling-body --medium --awake
/tmp/gfx-circle-scale --count-600 --falling-body --medium --awake --mixed
silex compile Packages/GFX.Physics/Benchmarks/JointScale2D.sx --release -o /tmp/gfx-joint-scale
/tmp/gfx-joint-scale
/tmp/gfx-joint-scale --workers-4
```

Utilisez Release, un échauffement et des répétitions isolées. Comparez médiane
et dispersion sur la même machine. Une amélioration d’une scène ne se généralise
pas à une autre charge.

## Architecture du chemin chaud

Les corps éveillés sont rangés dans une liste contiguë réutilisable. Une grille
déterministe découvre les candidats dynamiques et un set ouvert déduplique les
paires. Les contacts persistants conservent leurs impulsions compatibles. Le
solver prépare des contraintes contiguës et les répartit en couleurs sans
conflit.

Le parallélisme utilise un executor persistant. Les seuils de 16 384 corps
actifs et 4 096 contraintes évitent de planifier les petites charges ; ils ne
sélectionnent jamais un autre algorithme. La douzième couleur de débordement
reste ordonnée et scalaire.

Le sommeil retire le fond calme des piles du chemin chaud. Les corps bullets et
flux d’événements restent opt-in. Le pas stabilisé n’alloue ni par contact ni
par job.

## Profil public

```silex
world.set_profiling_enabled(true)
world.step(1.0 / 60.0)
let profile = world.step_profile()
print(profile.broad_phase_ms)
```

Le profil expose seulement `motion_ms`, `broad_phase_ms`, `solve_ms`,
`sleep_ms` et `total_ms`. Activez-le uniquement pour diagnostiquer, car la
mesure a elle-même un coût.

## Isoler simulation et rendu

```text
silex compile Silex-Benchmarks/Sources/FallingBodies2D/Main.sx --release -o /tmp/gfx-falling-body
/tmp/gfx-falling-body --stress-5000 --smoke-30 --awake --batch-4 --immediate --no-panel
/tmp/gfx-falling-body --stress-5000 --smoke-long --render-only --immediate --no-panel
```

Le mode simulation et le mode `render-only` distinguent les limites de Physics,
Scene2D, Canvas et GPU. Les observations graphiques ne remplacent pas les
tests headless de correction.

## Règles d’acceptation

Une optimisation conserve déterminisme entre nombres de workers, intégrité des
handles, stabilité des contacts, bornes physiques et absence d’allocation
accidentelle. Les mesures Debug servent au diagnostic, jamais aux budgets de
cadence. Les résultats et configurations exactes appartiennent aux baselines
datées du dépôt.
