# CCD, capteurs et événements post-step

Les flux d’événements sont activés par corps ou collider afin qu’un monde
ordinaire ne construise aucun payload inutilisé.

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

Les bullets balaient chaque paire de colliders autorisée, et pas seulement la
forme primaire de chaque corps. Un corps composé ou un conteneur cinématique
conserve donc ses parois secondaires dans le CCD. Le premier impact de toutes
les paires admissibles est retenu, y compris avec raffinement rotationnel, et
une même paire de corps ne peut occuper qu’une entrée du cache de contacts.

Les capteurs signalent les transitions sans réponse. Les corps ordinaires ne
paient pas ce chemin général et un monde sans bullet le quitte immédiatement.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Events.sx
```
