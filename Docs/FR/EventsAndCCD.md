# CCD, capteurs et événements post-step

Les flux d’événements sont activés par collider afin qu’un monde ordinaire ne
construise aucun payload inutilisé. Les réglages du corps configurent son
collider implicite de compatibilité.

```silex
let trigger = Physics.RigidBody2DSettings()
    ..body_type = Physics.BodyType2D.fixed
    ..shape = Physics.Shape2D.box(Physics.Box2D(Math.Vec2(2.0)))
    ..is_sensor = true
    ..enable_sensor_events = true

let projectile = Physics.RigidBody2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.1))
    ..is_bullet = true
    ..enable_move_events = true
    ..enable_contact_events = true
    ..enable_hit_events = true
```

Les événements sont des buffers déterministes produits après le pas, jamais
des callbacks pendant le solver.

```silex
var began:Physics.ContactBeginEvent2D[] = []
var ended:Physics.ContactEndEvent2D[] = []
var hits:Physics.ContactHitEvent2D[] = []
var sensor_began:Physics.SensorBeginEvent2D[] = []
var sensor_ended:Physics.SensorEndEvent2D[] = []
var moves:Physics.BodyMoveEvent2D[] = []

world.step(1.0 / 60.0)
world.write_contact_begin_events(began)
world.write_contact_end_events(ended)
world.write_contact_hit_events(hits)
world.write_sensor_begin_events(sensor_began)
world.write_sensor_end_events(sensor_ended)
world.write_body_move_events(moves)
```

Les événements de contact et d’impact nomment les deux colliders exacts avec
`pair()`, `first_collider()` et `second_collider()`, tout en conservant l’accès
à leurs corps. Les événements capteur distinguent `sensor()` et `visitor()`.
Leur géométrie, matériau et identifiant applicatif sont des valeurs autonomes :
ils restent lisibles après destruction, tandis que le handle incorporé devient
invalide et refuse toute mutation.

`Collider2D.set_event_options(contact, hit, sensor)` modifie les flux entre
deux pas. Activer un flux sur une paire déjà présente produit un begin au pas
suivant ; le désactiver produit le end correspondant.

Les bullets balaient chaque paire de colliders autorisée, et pas seulement la
forme primaire de chaque corps. Un corps composé ou un conteneur cinématique
conserve donc ses parois secondaires dans le CCD. Le premier impact de toutes
les paires admissibles est retenu, y compris avec raffinement rotationnel, et
une même paire de corps ne peut occuper qu’une entrée du cache de contacts.

Tout collider convexe dynamique assez rapide balaie les formes fixes et
cinématiques autorisées. Une cible cinématique fournit son mouvement relatif
complet au sweep au lieu d’être traitée comme une téléportation. `is_bullet`
étend volontairement ce travail aux cibles dynamiques.

Le CCD évalue chaque paire de colliders, et pas seulement la forme primaire de
chaque corps. Le premier impact admissible est retenu, y compris avec
raffinement rotationnel, puis reçoit la réponse et les événements ordinaires.
Une même paire de corps ne peut occuper qu’une entrée du cache de contacts.
Les capteurs rapides signalent une traversée complète sans réponse physique.
Filtres, filter joints et côté unilatéral des chaînes restent identiques au
chemin discret. Les corps lents quittent le chemin avant toute recherche de
paire, et seules les bullets paient les tests dynamique contre dynamique.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Events.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContactSnapshots.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContinuousCollision.sx
```

La comparaison sur un pas avec Box2D 3.1.1, y compris les divergences de
réponse documentées, est décrite dans
[`../Benchmarks/Oracle2D/README.md`](../../Benchmarks/Oracle2D/README.md).
