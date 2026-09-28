# Géométrie convexe 3D autonome

`GFX.Physics` fournit des sphères, des boîtes, des capsules et des poses rigides en valeurs
Silex. Leurs requêtes de distance, recouvrement et rayon fonctionnent sans
monde, scène ni renderer. Le [monde 3D](World3D.md) utilise ces premières
formes pour le mouvement libre des corps.

```silex
use GFX.Physics
use STD.Math

let sphere = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
let box = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0, 1.0, 3.0)))
let capsule = Physics.Shape3D.capsule(Physics.Capsule3D(0.25, 0.5))
let pose = Physics.Transform3D(
    position:Math.Vec3(2.0, 3.0, 4.0),
    rotation:Math.Quat.angle_axis(Math.half_pi(), Math.Vec3.up())
)
let point = pose.point(Math.Vec3.right())
assert(pose.inverse_point(point).nearly_equal(Math.Vec3.right(), 0.00001))

let placed_sphere = Physics.ShapePlacement3D(sphere)
let placed_box = Physics.ShapePlacement3D(box, pose)
let gap = Physics.Geometry3D.distance(placed_sphere, placed_box)
let touching = Physics.Geometry3D.overlaps(placed_sphere, placed_box)
let hit = Physics.Geometry3D.ray_cast(
    Physics.Ray3D(Math.Vec3(-4.0, 3.0, 4.0), Math.Vec3(8.0, 0.0, 0.0)),
    placed_box
)
```

`Box3D` reçoit les dimensions complètes, centrées sur l'origine locale ;
`half_size()` retourne les demi-dimensions. `Sphere3D` reçoit un rayon positif.
`Capsule3D(radius, half_height)` entoure un segment local vertical de longueur
`2 × half_height` ; sa hauteur totale vaut `2 × (half_height + radius)`.
Les trois formes refusent les valeurs non finies ou non positives. Une
`Transform3D` conserve une position finie et un quaternion unitaire. Ses
opérations `point` et `vector` appliquent la rotation ; `point` ajoute aussi la
translation. `inverse_point` et `inverse_vector` défont ces opérations.
Un quaternion déjà proche de l'unité est normalisé après vérification ; un
quaternion nul, non fini ou éloigné de l'unité est rejeté.

La convention est celle de `STD.Math` : repère droit, Y vers le haut. La pose
est sans échelle ; les dimensions appartiennent à la forme. Les transformations
ne corrigent pas silencieusement un quaternion invalide.

## Résultats des requêtes

`Geometry3D.distance(first, second)` accepte toute paire de sphères, boîtes
et capsules, y compris les poses orientées. `DistanceResult3D.separation` est positive
quand les surfaces sont distinctes, nulle à la tangence et négative en
pénétration. `normal` est une direction unitaire de la première forme vers la
seconde. Les deux points témoins appartiennent aux surfaces respectives.
Quand plusieurs points sont également proches, leurs coordonnées peuvent
différer sans changer la séparation. En pénétration ou en inclusion, la
différence des témoins ne représente pas nécessairement la profondeur ; lire
`separation` directement. Une paire de sphères concentriques choisit +X comme
normale déterministe.

`Geometry3D.overlaps` traite la tangence comme un recouvrement. Pour deux
boîtes, il utilise les axes séparateurs sans calculer tous les points les plus
proches. `Ray3D(origin, translation)` décrit un segment paramétré de 0 à 1 ;
son origine et sa translation doivent être finies, et la translation non
nulle. `Geometry3D.ray_cast` retourne `hit`, le premier `fraction` rencontré,
le point et la normale extérieure de la forme. Depuis l'intérieur d'une
forme, le premier passage sortant est retourné. Un rayon manqué a `hit = false`.

Le cas de boîte/boîte séparée évalue sommets contre faces puis arêtes contre
arêtes. Les capsules utilisent le segment axial et les rayons testent aussi
leurs hémisphères. Les requêtes n'allouent pas de cache persistant ; le monde
sélectionne les paires candidates avant ces requêtes fines. Les autres familles
de formes, les casts de formes et les requêtes sur
le monde restent à livrer.
