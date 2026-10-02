# Géométrie 3D autonome

`GFX.Physics` fournit des sphères, des boîtes, des capsules, des triangles, des composés immuables et des poses rigides en valeurs
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
et capsules, ainsi que sphère/triangle et sphère/maillage triangulaire dans les
deux ordres, y compris
les poses orientées. `DistanceResult3D.separation` est positive
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
le point et la normale extérieure de la forme (ou celle du côté touché pour un
triangle). Depuis l'intérieur d'une
forme, le premier passage sortant est retourné. Un rayon manqué a `hit = false`.

Un `Triangle3D(first, second, third)` porte trois sommets locaux finis et non
alignés. Leur ordre détermine la face avant par `(second - first) × (third -
first)` ; `normal()` retourne cette direction unitaire. La distance à une
sphère utilise le point le plus proche sur la face, une arête ou un sommet.
Elle est géométrique des deux côtés du triangle, comme `overlaps`. Le rayon
simple traverse et touche les deux faces ; sa normale est opposée à sa direction
sur la face touchée. La réponse du monde est unilatérale, décrite dans
[World3D](World3D.md). Les autres paires avec un triangle et les composés de
triangles ne sont pas pris en charge.

`TriangleMesh3D([triangle, ...])` copie une liste non vide de `Triangle3D`.
L'index de chaque triangle, à partir de zéro, reste son identité tant que le
maillage n'est pas remplacé. `triangle_count()` et `triangle(index)` permettent
de consulter cette liste. La distance à une sphère choisit la plus petite
séparation ; en cas d'égalité, elle conserve le premier index. Cet index est
renvoyé par `second_child_id` ou `first_child_id` selon l'ordre des formes ; un
rayon le renvoie par `child_id`. Distance, recouvrement et rayon autonomes
restent géométriques des deux côtés. Les autres paires avec un maillage ne
sont pas prises en charge.

Le cas de boîte/boîte séparée évalue sommets contre faces puis arêtes contre
arêtes. Les capsules utilisent le segment axial et les rayons testent aussi
leurs hémisphères. Les requêtes n'allouent pas de cache persistant ; le monde
sélectionne les paires candidates avant ces requêtes fines. Les autres familles
de formes, les casts de formes et les requêtes sur
le monde restent à livrer.

## Composé immuable

`Compound3D` prend un tableau non vide de `CompoundChild3D(id, shape,
transform)`. Chaque enfant possède un identifiant entier positif ou nul,
unique dans le composé, et une pose locale. Les enfants peuvent être des
sphères, boîtes ou capsules ; un composé imbriqué est rejeté. La liste est
copiée à la construction et ne peut plus être modifiée. La pose effective
applique d'abord la pose de l'enfant, puis celle du composé.

```silex
use GFX.Physics
use STD.Math

var compound = Physics.Compound3D([
    Physics.CompoundChild3D(22,
        Physics.Shape3D.sphere(Physics.Sphere3D(0.5)),
        Physics.Transform3D(position:Math.Vec3(2.0, 0.0, 0.0)))
])
let target = Physics.ShapePlacement3D(
    Physics.Shape3D.compound(compound)
)
let probe = Physics.ShapePlacement3D(
    Physics.Shape3D.sphere(Physics.Sphere3D(0.5)),
    Physics.Transform3D(position:Math.Vec3(4.0, 0.0, 0.0))
)
let result = Physics.Geometry3D.distance(probe, target)
assert(result.second_child_id == 22)
```

Distance et recouvrement parcourent les enfants et retiennent la plus petite
séparation signée. `first_child_id` et `second_child_id` donnent les enfants
sélectionnés, ou `-1` pour une forme primitive. Pour un rayon, `child_id`
identifie le premier enfant touché, ou vaut `-1` en cas d'échec ou de cible
primitive. Les égalités conservent le premier enfant dans l'ordre fourni.
Un composé peut participer aux requêtes autonomes des deux côtés ; sa prise
en charge comme corps est décrite dans le [monde 3D](World3D.md).
