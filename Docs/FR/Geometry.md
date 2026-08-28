# Géométrie et requêtes de collision

`Physics.Geometry2D` fournit distance, recouvrement, manifold, ray cast et
shape cast sur des `ShapePlacement2D` transformés et filtrés.

```silex
use GFX.Physics
use STD.Math

let player = Physics.ShapePlacement2D(
    Physics.Shape2D.capsule(Physics.Capsule2D(
        Math.Vec2(0.0, -0.5),
        Math.Vec2(0.0, 0.5),
        0.25
    )),
    Physics.Transform2D(position:Math.Vec2(2.0, 3.0))
)
let wall = Physics.ShapePlacement2D(
    Physics.Shape2D.box(Physics.Box2D(Math.Vec2(1.0, 4.0), 0.1))
)

let distance = Physics.Geometry2D.distance(player, wall)
let manifold = Physics.Geometry2D.manifold(player, wall)
let hit = Physics.Geometry2D.shape_cast(
    player,
    Math.Vec2(-4.0, 0.0),
    wall
)
```

Dimensions et rayons doivent être finis, les rayons positifs et les extrémités
distinctes. Un polygone accepte trois à huit points, soude les voisins proches,
construit leur hull convexe anti-horaire et refuse un résultat collinéaire. Une
chaîne exige quatre points et son côté solide se trouve à droite du parcours.

Les filtres utilisent catégories et masques 64 bits. Les groupes positifs
égaux forcent le contact, les groupes négatifs égaux l’interdisent. La distance
reste purement géométrique ; les autres requêtes appliquent les filtres.

Chaque appel possède son scratch et peut s’exécuter parallèlement aux autres.
Les algorithmes sont des adaptations Silex natives du hull, GJK, manifold et
casts de Box2D 3.1.1, utilisé seulement comme oracle différentiel.
