# Géométrie et requêtes de collision

`Physics.Geometry2D` fournit AABB, test et point le plus proche, distance,
recouvrement, manifold, ray cast et shape cast sur des `ShapePlacement2D`
transformés et filtrés.

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
let contains = Physics.Geometry2D.test_point(player, Math.Vec2(2.0, 3.0))
let closest = Physics.Geometry2D.closest_point(wall, Math.Vec2(4.0, 0.0))
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
Dans une chaîne ouverte, le premier et le dernier segment servent de géométrie
fantôme pour raccorder les normales aux extrémités : seuls les segments compris
entre eux collisionnent. Fournissez donc un point fantôme avant et après le
tracé collisionnel voulu.

Les filtres utilisent catégories et masques 64 bits. Les groupes positifs
égaux forcent le contact, les groupes négatifs égaux l’interdisent. La distance
reste purement géométrique ; les autres requêtes appliquent les filtres.

Chaque appel possède son scratch et peut s’exécuter parallèlement aux autres.
Les algorithmes sont des adaptations Silex natives du hull, GJK, manifold et
casts de Box2D 3.1.1, utilisé seulement comme oracle différentiel.

## Valeurs valides et mouvements dégénérés

Les positions, translations et angles doivent être finis. `Transform2D`
représente la rotation par un angle en radians : le consommateur ne fournit
pas de couple cosinus/sinus à normaliser. `AABB2D(center, half_size)` accepte
une demi-taille nulle, refuse les composantes négatives et vérifie que les
bornes calculées restent finies. Ses accesseurs centre/demi-taille évitent un
débordement intermédiaire lorsque les bornes sont représentables.

`Ray2D` accepte une translation nulle ou très courte. Sa fraction maximale
est finie et appartient à `[0, 100000)`. Une fraction nulle est valide. Le
segment interrogé va de `origin` à `origin + translation * max_fraction`.
`Geometry2D.shape_cast` et les requêtes de monde correspondantes acceptent
également un mouvement nul et une fraction maximale finie non négative.

Un rayon valide ne garantit pas un impact. Un départ strictement intérieur à
un cercle ou une capsule renvoie un impact à fraction zéro, au point de départ,
avec une normale nulle. Un polygone sans arrondi accepte aussi ses frontières
à fraction zéro. Pour un cercle ou une capsule, un rayon nul exactement sur la
frontière ne renvoie pas d’impact ; un rayon entrant peut y renvoyer une normale
de surface. Un rayon parallèle à un segment ne le touche pas. Les chaînes
conservent leur côté solide. Les arrondis polygonaux utilisent un shape cast
avec sa tolérance de contact.

Un shape cast en recouvrement initial renvoie une fraction et une normale
nulles, avec un point commun entre les témoins des formes. `can_encroach`
autorise une poursuite depuis certains recouvrements superficiels ; il ne
supprime pas les impacts initiaux profonds. Une normale nulle signale donc un
recouvrement initial sans direction d’entrée déterminée : ne pas l’utiliser
comme normale unitaire de surface. Quand `hit` vaut `false`, les autres champs
sont neutres et ne décrivent pas un contact.

Les plans de `CharacterMover2D` sont des résultats de collision :
`CharacterCollisionPlane2D` expose une normale normalisée, un point et une
séparation en lecture. Il n’existe pas de constructeur public de plan général.
Le package valide les valeurs à la frontière des constructeurs et opérations ;
il ne fournit pas de doublons des six helpers booléens de validation de Box2D.
Un argument invalide produit un diagnostic immédiatement.

Le témoin `GeometryValuesOracle2D.sx` est apparié à
`Oracle2D/GeometryValuesOracle.c` : 360 résultats de rayons et de shape casts,
avec translation nulle, fraction nulle, petite translation, frontières,
recouvrements, caps de capsules et décalage des formes. Le comparateur contrôle
les impacts exactement, et les fractions, points et normales avec des
tolérances absolue `2e-5` et relative `2e-6` ; les zéros des recouvrements sont
exacts. `GeometricValidityOracle.c` et `check-geometric-values.py` distinguent
les représentations brutes Box2D des entrées publiques Silex. Les tests
consommateurs vérifient aussi les rotations, plans produits et requêtes de monde.

## Provenance

Les adaptations proviennent principalement de `src/hull.c`, `src/distance.c`,
`src/geometry.c` et `src/manifold.c` au commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`. Les notices de copyright d’Erin
Catto et la licence MIT sont conservées dans `Box2D-NOTICE.txt` à la racine du
package. Aucun binaire Box2D n’entre dans le runtime de production.
