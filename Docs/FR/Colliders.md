# Colliders et matériaux

`RigidBody2D` possède mouvement et durée de vie. `Collider2D` possède géométrie,
densité, matériau, filtre, état de capteur et options d’événements. Leurs
handles n’exposent ni slot, ni génération, ni proxy, ni pointeur natif.

```silex
var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..create_implicit_collider = false
)

let material = Physics.PhysicsMaterial2D()
    ..friction = 0.8
    ..restitution = 0.2
    ..rolling_resistance = 0.05
    ..tangent_speed = 1.5
    ..application_id = Physics.PhysicsMaterialId2D(12)

var hull = world.create_collider(body, Physics.Collider2DSettings()
    ..shape = Physics.Shape2D.box(Physics.Box2D(Math.Vec2(2.0, 1.0)))
    ..density = 2.0
    ..material = material
)
var trigger = world.create_collider(body, Physics.Collider2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(1.0))
    ..is_sensor = true
    ..enable_sensor_events = true
)
```

Un corps peut avoir zéro, un ou plusieurs colliders. Le constructeur par défaut
crée un collider implicite compatible avec l’API historique. Les géométries,
matériaux, filtres et options sont modifiables lorsque le monde n’est pas
verrouillé, puis les données dérivées sont reconstruites avant `step`.

Détruire un collider invalide son handle. Détruire un corps invalide tous ses
colliders. Une chaîne peut définir un matériau commun ou exactement un matériau
par segment et reste limitée aux corps fixes.

La réponse friction/restitution complète concerne actuellement le collider
principal boîte/cercle. Les autres colliders participent au broad phase, aux
filtres, contacts géométriques et capteurs. La densité de chaque collider
contribue déjà à la masse, au centre de masse et à l’inertie composés du corps.
Résistance au roulement et vitesse tangentielle restent conservées pour les
jalons de réponse ultérieurs.
