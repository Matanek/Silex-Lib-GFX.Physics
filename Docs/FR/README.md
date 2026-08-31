# GFX.Physics

`GFX.Physics` est une extension officielle optionnelle de GFX. Son monde 2D
est utilisable sans fenêtre, renderer, scène ni ECS. Le cœur de simulation est
écrit en Silex natif ; Box2D 3.1.1 sert uniquement d’oracle différentiel.

```text
silex install GFX.Physics
```

## Corps et monde

```silex
use GFX.Physics
use STD.Math

var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.25))
    ..position = Math.Vec2(0.0, 10.0)
    ..rotation = 0.15
    ..friction = 0.75
)

world.step(1.0 / 60.0)
print(body.position())

world.destroy_rigid_body(body)
assert(!body.is_valid())
```

Les handles de corps, colliders et joints sont typés et générationnels. Leur
destruction invalide toutes les copies conservées. Le monde possède l’horloge,
les ressources de simulation et la frontière de mutation.

## Géométrie et contacts

Les formes comprennent boîtes, cercles, capsules, polygones convexes, segments
et chaînes. Les requêtes de distance, recouvrement, manifold, rayon et shape
cast sont pures et indépendantes d’un monde.

```silex
let capsule = Physics.ShapePlacement2D(
    Physics.Shape2D.capsule(Physics.Capsule2D(
        Math.Vec2(0.0, -0.5),
        Math.Vec2(0.0, 0.5),
        0.25
    ))
)
let wall = Physics.ShapePlacement2D(
    Physics.Shape2D.box(Physics.Box2D(Math.Vec2(1.0, 4.0), 0.1)),
    Physics.Transform2D(position:Math.Vec2(2.0, 0.0))
)
let hit = Physics.Geometry2D.shape_cast(
    capsule,
    Math.Vec2(4.0, 0.0),
    wall
)
```

Les contacts persistants sont des snapshots stables lus après `step` :

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)
print(world.contact_count())
```

La réponse dynamique Soft Step couvre toutes les formes publiques. Les
politiques de contact optionnelles sont évaluées avant le dispatch du solveur,
sur le thread qui possède `step`.

## Catalogues et parallélisme

Le package contribue ses types aux catalogues ouverts de GFX :

```silex
use GFX.Components
use GFX.Resources

let world = Resources.World2D()
let body:Components.RigidBody2D = world.create_rigid_body()
```

Un monde peut créer un executor persistant :

```silex
world.enable_parallelism(4)
```

Le nombre de workers ne change ni les paires, ni le solver, ni l’ordre logique.
Les seuils ne modifient que la répartition du même travail.

## Guides

- [Architecture](Architecture.md)
- [Intégration Application, ECS et Scene2D](ApplicationIntegration.md)
- [Masse, forces et contrôle des corps](BodyControl.md)
- [Colliders et matériaux](Colliders.md)
- [Contrat de complétude Box2D](Completeness.md)
- [Contacts persistants](Contacts.md)
- [Filtrage avancé et pré-solve](ContactPolicies.md)
- [Événements, capteurs et CCD](EventsAndCCD.md)
- [Requêtes géométriques](Geometry.md)
- [Îlots actifs et sommeil](Islands.md)
- [Joints, moteurs et ressorts](Joints.md)
- [Réglages et compteurs du monde](WorldSettings.md)
- [Migration de 0.4 vers 0.5](Migration.md)
- [Corpus oracle et budgets](OracleAndBudgets.md)
- [Contrat de performance](Performance.md)

L’exemple visuel central se lance depuis la racine :

```text
silex run Silex-Examples/Sources/RotatingPhysicsContainer/Main.sx --release
```
