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

`RigidBody2D.set_contact_events_enabled(enabled)` et
`set_hit_events_enabled(enabled)` règlent respectivement les contacts et les
impacts sur tous les colliders déjà attachés au corps. Les options capteur,
filtre personnalisé et pre-solve restent propres à chaque collider. Ces
mutations ne réveillent pas le corps et ne changent pas ses événements de
mouvement. Un collider ajouté ensuite conserve ses réglages de création.

`Collider2D.set_event_options(contact, hit, sensor)` permet un réglage
individuel entre deux pas. L’abonnement begin/end d’un contact existant est
conservé pendant la durée de vie du contact : activer ou désactiver l’option ne fabrique pas
de transition. Les nouveaux contacts prennent les options courantes ; les
impacts les relisent à chaque pas. Le flux capteur conserve sa sémantique
propre : l’activation sur un chevauchement présent produit un begin au pas
suivant, la désactivation son end. Toutes ces mutations refusent un handle
périmé ou un monde verrouillé pendant un pas ou un callback.

Le [scénario exécutable des options](../../Benchmarks/BodyEventsOracle2D.sx)
montre dix étapes, dont l’ajout d’un collider après mutation et les identités
des surfaces dans les événements.

Chaque paire de colliders solides possède son contact. Deux surfaces d’un même
corps peuvent toucher simultanément un autre corps, recevoir des décisions de
filtre ou de pre-solve distinctes et produire leurs propres événements. La
destruction d’une surface conserve les contacts des autres surfaces. Les
options begin/end sont capturées dès la création du contact potentiel, avant
le premier toucher visible.

Tout collider convexe dynamique assez rapide balaie les formes fixes et
cinématiques autorisées. Une cible cinématique fournit son mouvement relatif
complet au sweep au lieu d’être traitée comme une téléportation. `is_bullet`
étend volontairement ce travail aux cibles dynamiques.

Le CCD évalue chaque paire de colliders, et pas seulement la forme primaire de
chaque corps. Le premier impact admissible est retenu, y compris avec
raffinement rotationnel, puis reçoit la réponse et les événements ordinaires.
Le CCD réutilise le contact de la paire de colliders réellement touchée.
Les capteurs rapides signalent une traversée complète sans réponse physique.
Filtres, filter joints et côté unilatéral des chaînes restent identiques au
chemin discret. Les corps lents quittent le chemin avant toute recherche de
paire, et seules les bullets paient les tests dynamique contre dynamique.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/CompoundContacts.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/BodyEvents.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Events.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContactSnapshots.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContinuousCollision.sx
```

La comparaison sur un pas avec Box2D 3.1.1, y compris les divergences de
réponse documentées, est décrite dans
[`../Benchmarks/Oracle2D/README.md`](../../Benchmarks/Oracle2D/README.md).
