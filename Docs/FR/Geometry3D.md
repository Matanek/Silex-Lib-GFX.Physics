# Géométrie 3D autonome

`GFX.Physics` fournit des sphères, des boîtes, des capsules, des cylindres et formes effilées, des enveloppes convexes, des triangles, des plans, des maillages, des composés immuables et des poses rigides en valeurs
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

## Plan et demi-espace

`Plane3D(normal:Math.Vec3.up(), offset:0.0)` définit le demi-espace local
`normal.dot(point) <= offset`. La direction finie non nulle est normalisée ;
`offset` reste la distance signée en unités de longueur sur cette direction.
`Plane3D(Math.Vec3(0.0, 2.0, 0.0), 1.0)` a donc sa surface à `y=1`.
La pose transforme ce plan, sans lui donner une taille ni une épaisseur.

```silex
use GFX.Physics
use STD.Math

func main() {
    let floor = Physics.ShapePlacement3D(Physics.Shape3D.plane(Physics.Plane3D()))
    let cast = Physics.ShapeCast3D(Physics.ShapePlacement3D(
        Physics.Shape3D.cylinder(Physics.Cylinder3D(0.5, 0.5)),
        Physics.Transform3D(Math.Vec3(10000.0, 2.0, 0.0))), Math.Vec3(0.0, -4.0, 0.0))
    let hit = Physics.Geometry3D.shape_cast(cast, floor)
    assert(hit.hit && Math.abs(hit.fraction - 0.375) < 0.00001)
}
```

`Shape3D.plane` sert aux distances et recouvrements avec les volumes convexes
ou composés, et comme cible de rayon, balayage de sphère ou de forme convexe.
La distance prend le support le plus profond du volume vers le demi-espace,
avec projection sur le plan et normale du volume vers le plan. Un rayon
commencé dans le demi-espace occupé retourne `fraction=0`, son origine comme
point et la normale extérieure ; il ne recherche pas la sortie. Un balayage
déjà recouvrant retourne également une fraction nulle, avec point sur le plan.
Le plan ne peut pas être le volume mobile d'un ShapeCast3D.

Dans le monde, le plan doit appartenir à un corps fixe ; les corps dynamiques,
cinématiques, enfants de composé et distances plan/plan sont refusés.
Contacts, capteurs, filtres, mutations et CCD de translation visitent les
volumes ou feuilles de composé. Les caps plats et faces convexes conservent
jusqu'à quatre appuis ; aucun rayon géant ne limite la sélection des corps.
Le coût de sélection comprend chaque plan actif contre les corps activés.
Les coordonnées flottantes gardent leur précision habituelle : une surface
infinie ne supprime pas les limites numériques aux grandes coordonnées.

La géométrie analytique est infinie. Jolt épinglé utilise pour sa broad phase
une boîte virtuelle de demi-étendue configurable (1000 par défaut) et annonce
des contacts inconsistants près de cette frontière ; cette option interne
n'appartient pas à l'API Silex. Les témoins Jolt de requêtes sont qualifiés
à l'intérieur de cette zone, les contacts éloignés Silex indépendamment.

## Cylindres et formes effilées

`Cylinder3D(radius, half_height)` est un cylindre plein à caps plats, d’axe local
Y et de hauteur `2 × half_height`. Rayon et demi-hauteur sont finis et positifs.
`TaperedCylinder3D(top_radius, bottom_radius, half_height)` joint deux disques
par une surface conique ; un seul rayon peut être nul pour former un cône.
`TaperedCapsule3D(top_radius, bottom_radius, half_height)` est l’enveloppe
convexe de deux sphères centrées à `y=±half_height`, raccordées tangentiellement.
Ses rayons sont positifs et sa demi-hauteur peut être nulle. Si une sphère
contient l’autre, la géométrie devient cette sphère décalée. Les étendues
calculées doivent aussi rester finies.

```silex
use GFX.Physics
use STD.Math

func main() {
    let cylinder = Physics.Shape3D.cylinder(Physics.Cylinder3D(0.5, 0.5))
    let cone = Physics.Shape3D.tapered_cylinder(Physics.TaperedCylinder3D(0.0, 0.5, 0.5))
    let capsule = Physics.Shape3D.tapered_capsule(Physics.TaperedCapsule3D(0.25, 0.5, 0.5))
    let hit = Physics.Geometry3D.shape_cast(Physics.ShapeCast3D(
        Physics.ShapePlacement3D(cylinder, Physics.Transform3D(Math.Vec3(-3.0, 0.0, 0.0))),
        Math.Vec3(6.0, 0.0, 0.0)), Physics.ShapePlacement3D(cone))
    assert(hit.hit)
    var world = Physics.World3D()
    var body = world.create_rigid_body(Physics.RigidBody3DSettings() ..shape = capsule)
    print(body.mass_properties().local_center.y)
}
```

Les variantes `Shape3D.cylinder`, `tapered_cylinder` et `tapered_capsule` servent
aux corps fixes, cinématiques et dynamiques, aux enfants composés et aux
requêtes autonomes ou filtrées du monde. Rayons et balayages gardent la vraie
surface ronde ; aucune enveloppe à facettes ne remplace la collision. Les
requêtes avec triangles et maillages sont bilatérales ; leurs contacts physiques
respectent la face avant. Un cap plat utilise jusqu’à quatre contraintes
préparées depuis ses points d’appui et découpées par la surface rencontrée.
Les maillages gardent les deux appuis distincts d’une vallée ; les réactions
identiques aux coutures ou sur une crête sont fusionnées. Les caps sphériques
exposés d’une capsule effilée gardent leur normale analytique sur les arêtes.

La séparation extérieure est euclidienne ; en pénétration, l’axe indique la
translation minimale estimée pour séparer les volumes (`premier` déplacé à
l’opposé de la normale). Les inclusions sphère/forme axiale, sphère/boîte et
capsule/boîte suivent cette convention. Les requêtes par support sont normalisées à l’étendue commune : convergence de
distance à `10⁻⁷`, pénétration à `10⁻⁵`, tangence classée dans `10⁻⁶`. Les
balayages axiaux utilisent la surface continue,
avec une marge `10⁻⁶` de cette étendue. La qualification couvre les paires
obliques, caps, raccords, inclusions et témoins sur les deux surfaces ; elle
n’établit pas une garantie pour tous les floats ou des coordonnées extrêmes.

Les masses, centres et inerties sont ceux du solide homogène, intégrés sur ses
sections circulaires. La pose conserve l’origine des deux caps ; elle peut donc
différer du centre de masse. Cette masse géométrique de capsule effilée diffère
de l’approximation par boîte employée par Jolt. Les limites cylindre égal,
cône, capsule égale et sphère contenante sont qualifiées. Une masse ou inertie
automatique hors plage est rejetée pour un corps dynamique ; un corps fixe ou
cinématique et une masse explicite restent disponibles comme pour les convexes.

## Enveloppes convexes

`ConvexHull3D(points)` construit un solide fermé depuis au moins quatre points
finis non coplanaires. `Shape3D.convex(hull)` conserve cette enveloppe immuable.
Les points dupliqués, intérieurs ou redondants sur une face ne créent pas de
faces superposées. Les nuages dégénérés, les calculs non finis et les frontières
numériquement ambiguës sont rejetés. La construction utilise une tolérance de
1 millionième de l’étendue du nuage ; elle convient à de petits nuages préparés
au démarrage. Le package ne fournit pas encore une construction de gros assets.

La paire sphère/convexe accepte les deux ordres, les poses orientées et les
contacts de face, d’arête et de sommet. Depuis l’intérieur, la séparation vaut
l’opposé de la distance au plan de sortie le plus proche, moins le rayon ; la
normale géométrique pointe vers cette sortie. Cette exception historique
sphère/convexe diffère des inclusions dans une boîte ; le monde
emploie la normale de réponse correspondante pour expulser la sphère.
Les rayons sont découpés par les demi-espaces du solide et retournent la sortie
quand leur origine est intérieure. `triangle_count()` et `triangle(index)`
exposent la frontière triangulée orientée vers l’extérieur pour la visualiser.

La paire boîte/convexe utilise la frontière du solide dans les deux ordres.
Sa séparation extérieure est euclidienne ; en pénétration, elle mesure la
translation minimale le long d’un axe séparateur, y compris lorsqu’une boîte
est entièrement incluse. Les contacts de face utilisent jusqu’à quatre points
sur le polygone réel, indépendamment des diagonales de la triangulation.
Une boîte enfant d’un composé suit le même parcours.

La paire capsule/convexe utilise le segment axial entier : sa distance
extérieure est euclidienne, et sa pénétration mesure la translation nécessaire
pour sortir le segment et son rayon du solide. Une capsule oblique qui traverse
l’enveloppe reste traitée comme un solide, même si ses deux extrémités sont
extérieures. Une capsule parallèle à une face utilise deux points découpés par
le polygone réel, y compris lorsque ses extrémités dépassent les bords.
Une capsule enfant d’un composé utilise la même paire.

La paire convexe/convexe utilise les deux frontières dans les deux ordres.
La distance extérieure est euclidienne, y compris entre des arêtes obliques.
En pénétration ou inclusion, la séparation mesure la plus courte translation
séparatrice parmi les normales de faces et les axes croisés des arêtes.
Les contacts de face gardent jusqu’à quatre points sur leurs polygones réels ;
un contact d’arêtes utilise les témoins de leurs segments supports.
En cas de minima égaux, le moteur choisit un axe déterministe.

La paire convexe/triangle est bilatérale dans les requêtes autonomes. Sa
séparation extérieure est euclidienne aux faces, arêtes et sommets ; une
pénétration utilise la plus courte translation séparatrice des axes de faces
et d’arêtes. Le monde applique la politique de face avant du triangle fixe,
avec jusqu’à quatre points couvrant le polygone d’appui réel. Les capteurs,
requêtes de monde et CCD de translation utilisent la même paire. Un centre
volumique géométrique, indépendant de l’origine locale et des propriétés de
masse explicites du corps, détermine le côté du plan. Une enveloppe décalée
reste donc équivalente après compensation de sa pose.

La paire convexe/maillage utilise ces mêmes triangles dans les deux ordres.
La distance bilatérale conserve la séparation minimale et l’index de sa face ;
en cas d’égalité, le premier index est retenu. Dans le monde, les triangles
coplanaires partagent un appui couvrant jusqu’à quatre points, tandis que les
pans distincts d’une vallée gardent leurs deux réactions. Les réactions
identiques d’une crête sont fusionnées. Une ouverture sans triangles laisse
passer un convexe plus étroit ; les bords présents restent des appuis réels.
Voir [les contacts de terrain](World3D.md) pour la politique avant/arrière.

Une enveloppe peut être la forme d’un corps **fixe, cinématique ou dynamique**.
Sa densité détermine la masse, le centre de masse local et le tenseur complet
d’un solide homogène ; voir [les commandes du corps](World3D.md#poses-masse-et-commandes).
La pose place toujours l’origine des points fournis, qui peut différer du
centre de masse. La frontière reste immuable ; `set_shape` remplace la forme
et recalcule les propriétés de masse d’un corps dynamique.

Les collisions face aux sphères, boîtes, capsules et autres convexes fonctionnent
dans les deux ordres, avec capteurs, filtres et CCD linéaire. Un convexe
cinématique peut pousser un corps dynamique. Une enveloppe peut également
être un enfant de composé fixe, cinématique ou dynamique ; sa pose locale
place l’origine des points, indépendamment du centre de son volume.
Cette qualification ne couvre pas le CCD rotationnel. `CharacterMover3D`
est qualifié sur les convexes fixes pour le déplacement et l’appui ; voir
[le guide du personnage](Character3D.md). La famille convexe demeure partielle.

La scène `Silex-Examples/Sources/Physics3D/ConvexHullScene.sx` montre
deux sphères, une boîte et une capsule qui tombent sur un coin construit avec six points, rebondissent, quittent sa
pente puis touchent le plateau inférieur. Elle démarre et recommence automatiquement.

La scène `Silex-Examples/Sources/Physics3D/MovingConvexScene.sx` montre deux
solides convexes en chute et rotation, dont un centre de masse décalé, ainsi
qu’une plateforme convexe cinématique portant une sphère. Espace met en pause,
R recommence et Échap ferme la scène.

La scène `Silex-Examples/Sources/Physics3D/ConvexPairsScene.sx` montre un
tétraèdre en rotation heurtant une base convexe dynamique et une plateforme
convexe cinématique soulevant un cube convexe. Toutes les formes physiques de
cette scène sont des enveloppes ; les commandes restent Espace, R et Échap.

`Silex-Examples/Sources/Physics3D/ConvexTriangleScene.sx` montre trois triangles
fixes distincts : chute et rotation d’un tétraèdre, appui d’un cube dont les
sommets locaux sont décalés, et cube traversant la face arrière avant de
retomber sur l’avant. Espace met en pause, R recommence et Échap ferme.

`Silex-Examples/Sources/Physics3D/ConvexMeshScene.sx` montre la traversée de
coutures planes par un cube décalé, l’appui d’un cube dans une vallée et la
chute en rotation d’un tétraèdre. Les triangles sont visibles grâce à leurs
teintes alternées ; Espace met en pause, R recommence et Échap ferme.

## Résultats des requêtes

`Geometry3D.distance(first, second)` accepte toute paire de sphères, boîtes
et capsules, ainsi que les paires sphère/triangle, capsule/triangle et
boîte/triangle et leurs variantes maillées, ainsi que sphère/convexe et
boîte/convexe, capsule/convexe, convexe/convexe, convexe/triangle et convexe/maillage, dans les
deux ordres, y compris les poses orientées. `DistanceResult3D.separation` est positive
quand les surfaces sont distinctes, nulle à la tangence et négative en
pénétration. `normal` est une direction unitaire de la première forme vers la
seconde. Les deux points témoins appartiennent aux surfaces respectives.
Quand plusieurs points sont également proches, leurs coordonnées peuvent
différer sans changer la séparation. En pénétration ou en inclusion, la
différence des témoins ne représente pas nécessairement la profondeur ; lire
`separation` directement. Une paire de sphères concentriques choisit +X comme
normale déterministe.

Depuis l’intérieur d’une boîte, les distances sphère/boîte et capsule/boîte
conservent la convention signée : déplacer la première forme à l’opposé de la
normale la fait sortir. Pour la capsule, la profondeur prend en compte le
segment entier et son rayon, y compris un axe incliné ou traversant la boîte.
Les normales des faces et celles des arêtes extrudées par le segment déterminent
la plus courte sortie ; la distance extérieure conserve son minimum euclidien.
Les [tests d’inclusion](../../Tests/Consumer/Tests/BoxInterior3D.sx) vérifient les
points témoins, l’inversion, les transformations communes et trois échelles.

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
La capsule utilise tout son segment axial : le plus proche témoin peut être
au milieu du segment, même si ses deux extrémités sont hors de la face. La
pénétration tient aussi compte du segment entier et du rayon. La boîte couvre
les contacts face/arête/sommet ; sa pénétration est la plus courte translation
séparatrice parmi les axes des faces et les axes croisés des arêtes. Ces distances
sont géométriques des deux côtés du triangle, comme `overlaps`. Le rayon
simple traverse et touche les deux faces ; sa normale est opposée à sa direction
sur la face touchée. La réponse du monde est unilatérale, décrite dans
[World3D](World3D.md). Les autres paires avec un triangle et les composés de
triangles ne sont pas pris en charge.

`TriangleMesh3D([triangle, ...])` copie une liste non vide de `Triangle3D`.
L'index de chaque triangle, à partir de zéro, reste son identité tant que le
maillage n'est pas remplacé. `triangle_count()` et `triangle(index)` permettent
de consulter cette liste. La distance à une sphère, une capsule, une boîte ou une enveloppe convexe
choisit la plus petite séparation ; en cas d’égalité, elle conserve le premier
index. Cet index est
renvoyé par `second_child_id` ou `first_child_id` selon l'ordre des formes ; un
rayon le renvoie par `child_id`. Distance, recouvrement et rayon autonomes
restent géométriques des deux côtés. Les autres paires avec un maillage ne
sont pas prises en charge.

Un trou se représente en omettant ses triangles. Sur un terrain plan fixe,
une boîte, une sphère ou une capsule plus étroite que l'ouverture tombe
librement, sans appui sur les faces absentes. Une boîte plus large peut
reposer sur les faces présentes autour du trou ; ses points de manifold
restent sur ces faces. Quitter un bord extérieur termine le contact puis
laisse le corps tomber. Ces cas sont qualifiés à 120 Hz sur une ouverture
carrée, y compris ordre des triangles inversé et rotation commune autour de Y.
Les trous de terrains au relief arbitraire restent à qualifier. Le CCD linéaire des
terrains fixes est décrit dans [World3D](World3D.md).

`TriangleMesh3D.from_height_grid(columns, rows, heights, column_spacing,
row_spacing, holes:[], diagonal:HeightGridDiagonal3D.column_to_row)` construit
un maillage fixe à partir d'une grille régulière. `heights` est rangé par lignes
Z puis colonnes X : l'échantillon `(column, row)` occupe
`(column × column_spacing, height, row × row_spacing)` dans le repère local.
Il faut au moins deux échantillons par axe, exactement `columns × rows`
hauteurs finies et des espacements positifs finis, indépendants sur X et Z.

Le masque optionnel `holes` contient un booléen par échantillon : `true`
supprime les triangles qui utilisent ce sommet. L'autre triangle d'une cellule
peut donc survivre. Le masque doit être vide ou compter autant d'éléments que
`heights` ; au moins un triangle doit rester. Les hauteurs masquées restent
finies. Sans masque, chaque cellule produit deux triangles vers le haut,
par lignes puis colonnes, d'IDs `2 × (row × (columns - 1) + column)` et cet ID
plus un. Avec masque, les IDs numérotent les faces survivantes dans cet ordre.

La diagonale par défaut relie le sommet de la colonne suivante à celui de la
ligne suivante. `HeightGridDiagonal3D.first_to_opposite` relie le premier
sommet au sommet opposé, comme le heightfield Jolt épinglé. Ce choix change
l'interpolation d'une cellule non plane et les triangles retirés par un trou.

```silex
use GFX.Physics
use STD.Math

func main() {
    var grid = Physics.TriangleMesh3D.from_height_grid(2, 2,
        [0.0, 0.0, 0.0, 0.0], 1.25, 2.0,
        holes:[true, false, false, false])
    assert(grid.triangle_count() == 1)
    var world = Physics.World3D()
    var floor = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..shape = Physics.Shape3D.mesh(grid))
    floor.set_shape(Physics.Shape3D.mesh(Physics.TriangleMesh3D.from_height_grid(
        2, 2, [0.0, 0.0, 0.0, 0.0], 1.25, 2.0)))
}
```

Les triangles possèdent une géométrie immuable : modifier les tableaux sources
ne modifie pas le terrain. Reconstruire puis appeler `set_shape` remplace le
maillage et termine les contacts de l'ancienne révision. Le maillage reste
fixe, exact et non compressé ; il ne fournit ni mise à jour quantifiée de
hauteurs ni terrain dynamique. Une grille entièrement trouée est refusée ;
retirer le corps du monde pour retirer tout le terrain. Les requêtes parcourent
les faces, sans garantie de coût pour les très grands terrains.

Le cas de boîte/boîte séparée évalue sommets contre faces puis arêtes contre
arêtes. Les capsules utilisent le segment axial et les rayons testent aussi
leurs hémisphères. Les requêtes n'allouent pas de cache persistant ; le monde
sélectionne les paires candidates avant ces requêtes fines. Les
[balayages de volumes](#balayer-une-capsule-boîte-ou-enveloppe-convexe) et les
[requêtes du monde](World3D.md#interroger-les-corps-du-monde) sont disponibles.

## Balayer une sphère

Pour arrêter une sonde sphérique avant un obstacle, interrogez son volume :

```silex
use GFX.Physics
use STD.Math

func main() {
    let obstacle = Physics.ShapePlacement3D(Physics.Shape3D.box(
        Physics.Box3D(Math.Vec3(1.0))))
    let cast = Physics.SphereCast3D(Physics.Sphere3D(0.5),
        Math.Vec3(-3.0, 0.0, 0.8), Math.Vec3(6.0, 0.0, 0.0))
    let hit = Physics.Geometry3D.sphere_cast(cast, obstacle)
    assert(hit.hit)
    print(hit.fraction) // 0.35 : le volume touche l’arête ; son rayon central manque.
}
```

`SphereCast3D(sphere, origin, translation)` décrit une sphère translatée,
avec origine, extrémité et translation finies, translation non nulle et rayon
positif fini. `Geometry3D.sphere_cast(cast, target)` retourne le premier impact
dans `CastResult3D` : `hit`, `fraction` entre 0 et 1, `point` sur la cible,
`normal` unitaire sortante de la cible vers la sphère et `child_id`.
Le centre à l’impact vaut `origin + translation × fraction`. Une absence
retourne `hit = false` ; les autres champs n’ont alors pas de sens physique.

La cible peut être une sphère, boîte, capsule, enveloppe convexe, un triangle,
maillage ou composé qualifié. Faces, arêtes et sommets sont pris en compte,
y compris une tangence et l’extrémité du segment. Les triangles sont bilatéraux,
avec la normale du côté touché. L’index de face du maillage ou l’ID d’enfant du
composé est retourné ; une forme simple donne `-1`. À fraction strictement
égale, le premier enfant dans l’ordre de construction est conservé.

Un départ en recouvrement ou tangence donne **fraction zéro**, même si le
mouvement sort. Le point provient de la requête de distance ; pour un centre
inclus dans une boîte ou un convexe, la normale suit sa face de sortie la plus
proche. Les configurations concentriques et les faces également proches ont
un témoin déterministe, sans garantie de récupération physique complète.

La cible reste immobile pendant la requête. Il n’y a ni balayage de rotation,
ni déplacement implicite de corps. Pour les autres volumes convexes, voir
[leur balayage](#balayer-une-capsule-boîte-ou-enveloppe-convexe).
Les maillages et convexes parcourent leur frontière par requête ; les très
grands terrains ne sont pas qualifiés par cette API. Les témoins numériques
couvrent les échelles 0,1, 1 et 10, avec poses rigides et sommets décalés
compensés ; ils ne constituent pas une borne pour toutes les coordonnées
float possibles. Pour filtrer les corps d’un monde, voir [World3D](World3D.md#interroger-les-corps-du-monde).

## Balayer une capsule, boîte ou enveloppe convexe

Pour déplacer un volume jusqu'au premier obstacle, décrivez sa pose initiale
et sa translation dans `ShapeCast3D(placement, translation)` :

```silex
use GFX.Physics
use STD.Math

func main() {
    let obstacle = Physics.ShapePlacement3D(Physics.Shape3D.box(Physics.Box3D()))
    let probe = Physics.ShapePlacement3D(Physics.Shape3D.capsule(
        Physics.Capsule3D(0.5, 0.5)), Physics.Transform3D(Math.Vec3(-3.0, 0.0, 0.8)))
    let cast = Physics.ShapeCast3D(probe, Math.Vec3(6.0, 0.0, 0.0))
    let hit = Physics.Geometry3D.shape_cast(cast, obstacle)
    assert(hit.hit)
    print(hit.fraction) // 0.35
}
```

`Geometry3D.shape_cast(cast, target)` retourne `CastResult3D` avec les mêmes
champs et conventions que le balayage de sphère. La pose à l'impact conserve
`placement.transform().rotation` et sa position vaut
`placement.transform().position + translation × fraction`. La translation doit
être finie, non nulle, de longueur au carré finie, et son extrémité doit rester
finie. Le volume mobile peut être une sphère, capsule, boîte, cylindre,
cylindre effilé, capsule effilée ou enveloppe convexe ; triangle, maillage et composé mobiles sont rejetés par le constructeur.

Toutes les familles de cibles actuelles sont acceptées, y compris les triangles
bilatéraux, maillages et composés. Le premier obstacle et son `child_id` sont
conservés ; une égalité stricte conserve l'ordre de construction. Une requête
commençant en recouvrement ou tangence donne fraction zéro, même si elle sort.
Le témoin de distance initial est déterministe ; il ne représente pas une
récupération complète de pénétration profonde. Au contact, plusieurs points ou
normales peuvent être géométriquement valides : aucune unicité n'est promise.

La cible et l'orientation du volume restent fixes. Les sphères réemploient les
balayages analytiques ; les autres paires avancent selon leurs plans séparateurs
ou distances, avec une marge de convergence de `10⁻⁷` fois l'étendue du volume
mobile. Les tangences arrondies peuvent donc être signalées légèrement avant
le contact exact. La qualification couvre fractions à `0,0002`, normales à
`0,002`, échelles 0,1/1/10, poses indépendantes, décalages compensés et trajets
linéaires de 2 000 unités. Elle n'établit pas une borne pour toutes les valeurs
float ni pour de très grands terrains. Les requêtes parcourent les feuilles de
la cible et ne modifient aucun corps. Voir
[les requêtes filtrées du monde](World3D.md#interroger-les-corps-du-monde).

## Composé immuable

`Compound3D` prend un tableau non vide de `CompoundChild3D(id, shape,
transform)`. Chaque enfant possède un identifiant entier positif ou nul,
unique dans le composé, et une pose locale. Les enfants peuvent être des
sphères, boîtes, capsules, cylindres, formes effilées ou enveloppes convexes ; les triangles, maillages
et composés imbriqués sont rejetés. La liste est
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
