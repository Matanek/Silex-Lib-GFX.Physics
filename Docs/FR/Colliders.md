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

Le solver sélectionne le matériau du collider effectivement touché. Pour une
chaîne, il sélectionne celui du segment retenu par le manifold. La friction se
combine géométriquement, la restitution conserve la valeur la plus élevée et
les vitesses tangentielles s’additionnent. La résistance au roulement retient
le plus grand coefficient, pondéré par le plus grand rayon de contact, puis
limite la rotation relative. Ces règles s’appliquent aux cercles, capsules, segments,
polygones convexes ou arrondis et chaînes unilatérales dans le même graphe Soft
Step.
