# Simuler des corps rigides en 3D

`World3D` simule des corps fixes, cinématiques et dynamiques sans fenêtre,
scène, renderer ni ECS. Il accepte les sphères, boîtes, capsules, cylindres,
solides effilés et enveloppes convexes de `Shape3D`, avec contacts entre ces
formes. Les appuis de boîtes sur
des faces presque parallèles utilisent plusieurs points. Le balayage linéaire
des corps dynamiques est disponible sur demande pour les mouvements rapides.

Un `Triangle3D` peut être la forme d'un corps **fixe**. Il répond aux sphères,
capsules, boîtes et enveloppes convexes dynamiques du côté avant défini par l'ordre de ses sommets, y compris aux arêtes
et sommets isolés ; une forme dont le centre est derrière le plan du triangle
ne crée pas de contact. Le triangle et sa pose peuvent être remplacés sans
recréer le corps. Les corps triangulaires dynamiques ou cinématiques et les
triangles enfants d’un composé sont rejetés. Les contacts triangle/triangle,
les autres coutures et les terrains généraux restent à qualifier. Le CCD
linéaire sur face avant est qualifié ci-dessous. Un triangle physique reste
indépendant de la géométrie de rendu.

Pour un convexe, le centre qui sélectionne la face avant est celui du volume
homogène de l’enveloppe, indépendamment de son origine locale et d’une masse
explicitement fournie. Le contact de face couvre jusqu’à quatre points.
Ces règles s’appliquent aussi à un maillage fixe. Une enveloppe convexe
utilise plusieurs appuis quand leurs normales ou plans diffèrent, comme une
boîte. Les coutures planes sont regroupées et les points couvrent les
triangles réellement touchés. Repos, traversée sans friction, vallée de pente
±0,25, crête et passage dans une ouverture plane sont qualifiés, y compris
les deux ordres et une origine locale décalée. Les plis arbitraires, terrains
mobiles restent à qualifier ; les limites du CCD en rotation sont décrites
ci-dessous.
`Physics3D/ConvexMeshScene.sx` présente les coutures planes et la vallée.

`TriangleMesh3D` assemble plusieurs triangles dans une seule forme fixe. Pour
chaque sphère ou capsule dynamique primitive ou enfant de composé,
le monde ne produit qu’un contact au plus par pas, identifié par la face avant
retenue pour la séparation. Une boîte peut avoir plusieurs contacts de surface
simultanés lorsque leurs normales ou leurs plans d’appui diffèrent.
`Contact3D.first_child_id()` ou
`second_child_id()` indique son index. Un carré de deux triangles coplanaires
conserve l'appui pendant le franchissement de sa diagonale. La sélection
déterministe évite deux corrections identiques sur cette couture plane.
Une première cassure de hauteur de 0,4 m entre deux triangles est également
qualifiée pour une sphère sans friction : montée et descente dans les deux
sens gardent un contact pendant la couture et une trajectoire proche de Jolt.
Une grille régulière de hauteurs peut aussi produire ce maillage : une sphère
sans friction traverse les trois rangées inclinées d'une grille 4 × 4 dans
les deux sens, avec des trajectoires comparées à Jolt Debug et Release et une
identité de face suivie. La comparaison n'établit pas les coutures de hauteur
ou d'angle arbitraire ni les maillages non manifold. Les trous plans sont
qualifiés dans [Geometry3D](Geometry3D.md). Un corps maillé dynamique/cinématique
et un maillage enfant de composé sont absents. Une capsule dynamique verticale
repose sur une grille plane ;
une capsule parallèle à la face utilise deux points de contact lorsque ses
deux extrémités partagent la même normale et profondeur. Le parcours virtuel
des capsules sur les rangées inclinées est décrit dans [Character3D](Character3D.md).

Une boîte sur une couture coplanaire utilise jusqu’à quatre points couvrant
son empreinte sur les triangles touchés. Le contact conserve l’ID de la face
retenue pour la séparation. Le repos sans sommeil et le glissement sans
friction sur plusieurs cellules inclinées ont des témoins Jolt. Une petite
perturbation angulaire vérifie aussi le retour à l’appui stable.
Une vallée à deux pans de pente ±0,25 fournit deux réactions simultanées :
un cube de côté 1 m repose à hauteur de centre 0,625 m. Ce repos sans sommeil
est comparé à Jolt Debug/Release, dans les deux ordres de corps et de triangles,
ainsi que pour un enfant boîte de composé avec terrain tourné autour de Y. Les coutures
coplanaires et les réactions identiques d’une crête partagent un seul contact ;
chaque contact conserve l’ID d’un triangle représentatif. Les capteurs exposent
ces surfaces sans réponse. Cette qualification ne couvre pas tous les plis,
les trous ou les maillages non manifold.
La scène `Physics3D/BoxTerrainScene.sx` réunit pile au repos et glissement.

Un `Compound3D` immuable peut servir de forme à un corps fixe, cinématique ou
dynamique. Chaque paire d'enfants en contact possède son propre manifold,
avec `Contact3D.first_child_id()` et `second_child_id()` ; `-1` désigne une
forme primitive. Plusieurs contacts peuvent donc relier les mêmes corps.
Leurs événements et impulsions persistantes sont distingués par les deux
identités de corps et les deux IDs d'enfants, indépendamment de l'ordre de
construction du composé. Les capteurs exposent ces mêmes paires sans réponse.

Un composé cinématique emploie `move_kinematic` ou ses vitesses linéaire et
angulaire, comme les primitives. Ses enfants suivent la pose du parent ; leur
vitesse au contact inclut la rotation autour de l'origine du corps. Il peut
réveiller et transporter une charge dynamique. Un composé dynamique de boîtes,
sphères, capsules ou enveloppes convexes est également disponible :
la densité du corps appliquée à chaque enfant
détermine la masse, le centre de masse et le tenseur d'inertie du corps entier.
Les identités des enfants restent visibles dans les contacts. Le remplacement
de la forme d'un corps existant est disponible ; l'édition en place d'un
`Compound3D`, les autres familles géométriques et les terrains généraux
restent à livrer.
Le mouvement cinématique n'ajoute pas de CCD rotationnel.

Les enfants convexes conservent leur propre ID dans les distances, rayons,
contacts et événements. Leur centre volumique est transformé par leur pose
locale avant de combiner les masses ; le tenseur est tourné puis transporté
au centre commun. Un décalage des sommets compensé dans la pose de l’enfant
conserve ainsi la géométrie et la réponse du corps. Le CCD linéaire visite
les feuilles à rotation initiale conservée ; les appuis sur maillage gardent
l’ID de l’enfant et celui de la face, y compris lorsque les corps sont inversés.
La scène `Silex-Examples/Sources/Physics3D/ConvexCompoundScene.sx` montre
un composé de convexes et un composé mêlant tétraèdre et boîtes.

Le programme suivant applique une impulsion à une boîte, avance le monde et
lit sa position. L'impulsion est exprimée en masse × distance / seconde.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings()
        ..gravity = Math.Vec3())
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0))))
    body.apply_impulse(Math.Vec3(8.0, 0.0, 0.0))
    world.step(0.25)
    assert(body.position().nearly_equal(Math.Vec3(0.25, 0.0, 0.0), 0.00001))
    world.destroy_rigid_body(body)
    assert(!body.is_valid())
}
```

Un solide `Shape3D.convex(ConvexHull3D(points))` peut aussi être fixe,
cinématique ou dynamique et répondre aux sphères, boîtes, capsules et autres
enveloppes, ainsi qu’aux triangles et maillages fixes.
Voir les [enveloppes convexes et leurs limites](Geometry3D.md#enveloppes-convexes).
Une capsule couchée transversalement à une pente peut rouler sous l’effet de
la friction ; celle-ci ne garantit pas l’immobilité d’une forme arrondie.

Les [butées souples](HingeSoftLimits3D.md) amortissent les dépassements angulaires avec une raideur physique mutable.
La [commande combinée](HingeCombined3D.md) suit un angle et une vitesse actualisés ensemble.

## Poses, masse et commandes

Le repère suit `STD.Math` : droit, Y vers le haut. `Transform3D.position`
place l'origine de la forme ; `rotation` est un quaternion unitaire. Les
vitesses linéaire et angulaire sont exprimées dans le monde. `world_center_of_mass()`
retourne le centre de masse, qui peut différer de l'origine de la forme.
Les angles et vitesses angulaires sont en radians. `step(delta)` reçoit des
secondes et rejette une durée négative ou non finie.

Par défaut, un corps est dynamique, porte une sphère de rayon 0,5 et reçoit
une densité de 1. La masse et les moments d'inertie sont calculés pour la
sphère, la boîte, la capsule, l’enveloppe convexe ou un composé homogène de
primitives et de convexes. Un convexe utilise les moments volumiques de sa
frontière fermée :
son centre de masse peut être décalé et son tenseur peut avoir des termes
croisés, même sans rotation du corps. Les corps fixes et cinématiques ne
calculent pas de masse dynamique ; une masse explicite remplace le calcul
automatique à la création.
`MassProperties3D` accepte soit trois moments locaux positifs sous forme
`Vec3`, soit un tenseur symétrique défini positif sous forme `Mat3` ; les
anciens appels avec `Vec3` conservent leurs axes principaux locaux. Le champ
`inertia_tensor` restitue le tenseur complet, tandis que `local_inertia`
restitue sa diagonale. Pour un composé décentré ou orienté, les termes croisés
du tenseur influencent les impulsions et la rotation. Une
masse positive et un centre local peuvent aussi être fixés explicitement.
L'inertie est orientée dans le monde pour les couples et impulsions. Une
impulsion ou force avec un point d'application mondial produit aussi un
moment autour du centre de masse. `apply_torque` et
`apply_angular_impulse` agissent directement sur la rotation.

Un corps fixe garde sa pose et refuse forces et impulsions. Un corps
cinématique avance avec ses vitesses configurées ; `move_kinematic(target,
duration)` calcule des vitesses pour atteindre une pose à une date donnée,
puis les annule. La cible est atteinte exactement si un pas couvre la fin de
la durée. `set_transform`, `set_linear_velocity`,
`set_angular_velocity`, `set_enabled`, `set_shape` et `set_mass_properties` permettent les
changements directs. La masse ne peut être remplacée que sur un corps
dynamique.

`body.set_shape(new_shape)` remplace la forme sans changer l'identité, la pose,
les matériaux ou le filtre du corps. Pour modifier un composé, construire un
nouveau `Compound3D` puis le passer à cette méthode ; ses feuilles ne sont pas
modifiables en place. Sur un corps dynamique, la densité choisie à la création
recalcule la masse, le centre et le tenseur de la nouvelle forme. Un éventuel
`mass_properties` personnalisé est alors remplacé par ce calcul ; il peut être
réappliqué ensuite avec `set_mass_properties`. La vitesse linéaire est ajustée
pour conserver la vitesse du point correspondant au nouveau centre de masse,
et les corps concernés sont réveillés. Au pas suivant, les contacts de l'ancienne
forme se terminent et ceux de la nouvelle commencent, même si un ID d'enfant
est réutilisé ; aucune impulsion de l'ancienne forme n'est réemployée.

## Relier deux corps par une distance

`create_distance_constraint(first, second, settings)` relie deux ancrages
locaux appartenant au même monde. `DistanceConstraint3DSettings(longueur)`
impose d'abord une longueur exacte ; ses champs `minimum_length` et
`maximum_length` permettent aussi une plage. Les longueurs sont finies,
positives ou nulles et ordonnées. Au moins un corps doit être dynamique ; un
corps fixe peut servir d'ancrage au monde. Les contraintes actives partagent
les itérations de vitesse avec les contacts. À fréquence nulle, leur erreur
de position est aussi corrigée directement.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var anchor = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed
        ..transform = Physics.Transform3D(position:Math.Vec3(0.0, 3.0, 0.0)))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..transform = Physics.Transform3D(position:Math.Vec3(0.0, 1.0, 0.0)))
    var tether = world.create_distance_constraint(
        anchor, weight, Physics.DistanceConstraint3DSettings(2.0))
    world.step(1.0 / 60.0)
    assert(Math.abs(tether.current_length() - 2.0) < 0.01)
}
```

`spring_hertz` règle un ressort de distance en hertz ; zéro conserve la
contrainte rigide. `spring_damping_ratio` vaut zéro pour une oscillation peu
amortie, un pour l'amortissement critique et peut dépasser un. Les deux
valeurs doivent être finies et positives ou nulles. Le ressort peut agir sur
une longueur exacte ou sur les bornes d'une plage ; dans une plage, il reste
inactif entre les bornes. La correction rigide de position est désactivée
quand le ressort est actif afin de conserver son élasticité. Par exemple :

```silex
var settings = Physics.DistanceConstraint3DSettings(2.0)
settings.spring_hertz = 2.0
settings.spring_damping_ratio = 0.7
var tether = world.create_distance_constraint(anchor, weight, settings)
tether.set_spring(3.0, 1.0)
```

`first_local_anchor` et `second_local_anchor` déplacent les points d'attache
dans les repères locaux des corps. `current_length()` mesure leur écart
mondial. `reaction_force()` donne la force exercée sur le second corps pendant
le dernier pas positif, en masse × distance / seconde² ; elle vaut zéro pour
une contrainte inactive ou un pas sans impulsion. `set_limits(minimum, maximum)`,
`set_spring(hertz, damping_ratio)` et `set_enabled(enabled)` réveillent les corps
liés et effacent la réaction précédente. `destroy_distance_constraint` invalide
le handle ; détruire un corps lié invalide aussi ses contraintes.
`distance_constraint_count()` compte
les contraintes vivantes. Le pas nul conserve poses et observations.

## Relier deux corps par un point

`create_point_constraint(first, second, settings)` fait coïncider deux
ancrages locaux dans les trois directions tout en laissant leurs orientations
libres. `PointConstraint3DSettings()` place par défaut les deux ancrages à
l'origine locale de chaque corps ; renseigner `first_local_anchor` et
`second_local_anchor` pour viser un pivot réel. Les ancrages doivent être finis
et au moins un corps doit être dynamique. Les collisions entre les corps liés
restent actives : des ancrages qui imposent le chevauchement de leurs formes
peuvent opposer articulation et contact.

`anchor_error()` donne le vecteur allant du premier ancrage mondial au second.
`reaction_force()` donne la force exercée sur le second corps pendant le dernier
pas positif. `set_anchors(first, second)` et `set_enabled(enabled)` réveillent
les corps liés et effacent la réaction mémorisée. Le pas nul conserve les
observations. `destroy_point_constraint()` et la destruction d'un corps lié
invalident le handle ; `point_constraint_count()` compte les articulations
vivantes. L'articulation participe aux mêmes pas, contacts et îlots de sommeil
que la distance rigide.

La [charnière 3D](Hinge3D.md) maintient les ancrages et un axe de rotation,
avec des butées rigides et un moteur de vitesse. Le
[servo de charnière](HingePosition3D.md) approche un angle signé avec raideur,
amortissement et couple borné. Le ressort de distance est disponible ; les
autres familles d’articulations restent à livrer. Un choc très rapide peut
encore traverser un obstacle quand le balayage continu est désactivé, ce qui
est le réglage par défaut.

La [liaison fixe 3D](Fixed3D.md) conserve les six degrés de la pose relative de deux corps, avec capture de l’assemblage courant, repères locaux modifiables et réactions de force/couple.

La [glissière 3D](Slider3D.md) guide un chariot sur un rail tournant, avec course signée et butées rigides modifiables.

Le [moteur de glissière](SliderMotor3D.md) pilote une vitesse relative avec force maximale, freinage et mutation. Le [servo de position](SliderPosition3D.md) approche une course cible par ressort amorti physique.

Le [frein de glissière](SliderFriction3D.md) ralentit la course sans moteur avec une force maximale mutable.

Les [bornes de force signées](SliderForceBounds3D.md) règlent des efforts différents selon le sens, en vitesse et en position.

[Butées souples de glissière](SliderSoftLimits3D.md) : compression sous charge, ressort amorti, bornes égales et mutation.

Le [frein de charnière](HingeFriction3D.md) ralentit un axe sans moteur avec un couple borné, réglable à l’exécution.

Les [bornes de couple signées](HingeTorqueBounds3D.md) permettent un effort différent dans chaque sens, en vitesse ou en position.

## Interroger les corps du monde

`ray_cast(ray, ignore_body, filter)` retourne le premier impact de `Ray3D`, ou `null`.
`write_ray_hits(ray, output, ignore_body, filter)` remplit un tableau réutilisable avec
un impact par corps, classé par fraction croissante. Pour un composé, cet
impact est celui de son enfant le plus proche ; `child_id()` donne son ID et
vaut `-1` pour une primitive. Chaque `WorldRayHit3D` expose aussi `body()`,
`point()`, `normal()` et `fraction()` entre 0 et 1.

`shape_cast(cast, ignore_body, filter)` retourne `WorldCastHit3D?` pour une
capsule, boîte, enveloppe convexe ou sphère. `body()`, `point()`, `normal()`,
`fraction()` et `child_id()` suivent les conventions des autres impacts du
monde ; filtres, exclusion et durée de vie des snapshots sont identiques.
La pose initiale du volume est portée par `ShapeCast3D` et les corps sont
interrogés à leur pose courante, sans pas de simulation ni mutation. Voir
[le balayage de volume](Geometry3D.md#balayer-une-capsule-boîte-ou-enveloppe-convexe).

`sphere_cast(cast, ignore_body, filter)` retourne le premier impact du
volume de `SphereCast3D`, ou `null`. `WorldSphereHit3D` expose `body()`,
`point()`, `normal()`, `fraction()` et `child_id()` avec le contrat du
[balayage géométrique](Geometry3D.md#balayer-une-sphère). Les triangles restent
bilatéraux dans cette requête, indépendamment de la réponse physique du monde.
En cas d’égalité stricte, le premier emplacement vivant est conservé.
Cette opération n’avance pas le monde et ne modifie ni pose ni vitesse.

`write_overlaps(query, output, ignore_body, filter)` sélectionne les corps qui
recouvrent une `ShapePlacement3D`. Chaque `WorldOverlap3D` donne `body()`,
`query_child_id()` et `body_child_id()` ; les résultats suivent l'ordre des
emplacements du monde. Les corps désactivés sont exclus de ces requêtes.
L'argument facultatif `ignore_body` écarte un corps vivant du même monde,
par exemple l'émetteur d'un rayon. Un corps étranger ou détruit est refusé.

Le `QueryFilter3D` facultatif sélectionne les catégories par `mask_bits` et
inclut les capteurs par défaut ; `include_sensors:false` les écarte. Le masque
de contact d'un corps ne change pas les résultats des requêtes.

Les points, normales, fractions et ID copiés restent lisibles après les pas
suivants ou la destruction. Le handle `body()` garde son identité, mais
`is_valid()` devient faux lorsque son corps ou son monde disparaît. Ces
requêtes ne modifient pas les contacts.

## Collision continue linéaire

`RigidBody3DSettings.continuous_collision = true` active le balayage du corps
dynamique pendant chaque pas positif ; un corps fixe ou cinématique avec ce
réglage est refusé. `set_continuous_collision` le change à
l'exécution. Le réglage est désactivé par défaut. Le monde cherche le premier
impact le long de la translation relative avant de construire les contacts.
Un corps rapide peut ainsi atteindre un mur mince au lieu de le traverser ;
les filtres de paires s'appliquent aussi à cette recherche. Le même chemin
traite les obstacles fixes, cinématiques et dynamiques, puis laisse le solveur
répondre au contact. Une paire déjà recouvrante au début du pas suit la
résolution discrète habituelle.

Sur triangle et maillage fixes, une sphère, une boîte ou une capsule rapide
est arrêtée par une face avant et traverse les faces arrière ou les triangles
absents d'une ouverture. La sélection conserve le côté admissible au début
du balayage pour chaque face ; une face arrière proche ne masque pas une
face avant plus éloignée du même maillage. Les poses communes inclinées, les
ordres inversés, filtres et événements sont qualifiés, ainsi qu'une boîte
enfant de composé. Ces preuves concernent une translation linéaire à pose
fixe ; elles ne garantissent pas les plis arbitraires ni les appuis rasants.

Le CCD d’une enveloppe convexe est également qualifié contre un triangle
ou un maillage fixe : approche avant arrêtée, passage arrière libre, poses
communes inclinées, origine locale décalée, filtres et capteurs. Un triangle
arrière proche ne masque pas l’impact sur une face avant du même maillage.
Les limites du CCD en rotation sont décrites ci-dessous.

Pour un capteur entièrement traversé dans un seul pas, le monde émet un début
et une fin transitoires dans ce pas, sans contact persistant ni réponse.
Les faces arrière ne produisent pas d’événement transitoire ; leur recouvrement
initial ne masque pas une face avant traversée ensuite. L’émission transitoire
est un choix explicite : le témoin Jolt épinglé ne rapporte aucun événement
dans ce cas rapide, alors qu'il s'accorde avec Silex sur la traversée lente.

La recherche ne balaie que les translations avec les orientations du début
de pas. Elle ne garantit pas l'impact créé uniquement par une rotation rapide,
ni la chronologie exacte de plusieurs chocs successifs dans un même pas. La
rotation, les appuis rasants et les interactions entre plusieurs corps continus
restent à qualifier. Le temps d'impact sert à placer le premier contact ; le
solveur ne rejoue pas le temps restant du pas après ce choc.

## Sommeil et réveil

Un corps dynamique autorise le sommeil par défaut. Son
`sleep_threshold` vaut 0,05 pour les vitesses linéaire et angulaire ; il
doit être fini et positif ou nul. `allow_sleep`, `set_sleep_enabled`,
`set_sleep_threshold`, `is_awake` et `wake_up` pilotent ce contrat. Un corps
fixe ou cinématique n'est pas déclaré éveillé. Un corps libre sans gravité
peut dormir ; sous gravité, un îlot dynamique doit rester au contact d'un
corps fixe ou cinématique, par contact ou contrainte active, pour
s'endormir. Tous les corps d'un même îlot
atteignent ensemble un repos de 0,5 seconde au pas fixe avant de dormir.
Leurs vitesses deviennent alors nulles et leur pose cesse de dériver.

Une commande de vitesse, force, couple, impulsion, masse, pose ou matériau
réveille le corps concerné ; une modification de support peut réveiller les
autres corps du monde. Une collision nouvelle et le retrait d'un support
réveillent les corps concernés. Lorsqu'un corps d'un îlot est réveillé, le
réveil se propage par contact ou contrainte de distance, de point ou de
charnière au pas suivant. `step(0)` ne modifie ni le
sommeil ni les derniers contacts. Les contacts entre corps endormis restent
observables, avec une impulsion appliquée nulle pendant le pas inactif.

## Gravité et intégration

La gravité par défaut vaut `(0, -9.81, 0)`. `gravity_scale` est fixé par
corps à la création ; l'amortissement linéaire et angulaire est nul par
défaut. Les forces et couples s'accumulent jusqu'au prochain pas positif,
puis sont effacés. Un pas nul ne déplace aucun corps et conserve ces
accumulations. L'intégration utilise une vitesse semi implicite et maintient
un quaternion normalisé ; les résultats dépendent de la taille du pas.

## Lire les contacts

Chaque `RigidBody3DSettings` accepte un `collision_filter` et `is_sensor`.
`CollisionFilter3D(category_bits, mask_bits, group_index)` demande au moins
un bit de catégorie ; deux corps se rencontrent si chacun accepte la catégorie
de l'autre. Un même `group_index` non nul l'emporte : positif pour autoriser,
négatif pour interdire. `set_collision_filter` et `set_sensor` appliquent les
changements au prochain pas positif. Un capteur détecte le recouvrement sans
impulsion ni correction de position ; `Contact3D.is_sensor()` le signale et
son manifold est vide. La mutation du mode capteur termine l'ancienne paire
et en commence une nouvelle au pas suivant. Les capteurs ne propagent pas le
sommeil entre corps.

Après un pas positif, `contact_count()` compte les paires détectées et
`write_contacts(output)` copie leurs observations dans un tableau du
consommateur. Chaque `Contact3D` expose les deux handles, le centroïde des
points du manifold comme point représentatif, la normale de réponse, la
séparation mesurée avant correction et la somme des impulsions normales
appliquées. `point_count()` et
`write_points(output)` donnent les points du manifold ; chaque
`ContactPoint3D` contient une position dans le monde et ses impulsions normale
et tangentielle. Une séparation négative désigne une pénétration ; le pas
ramène alors les corps dynamiques vers la tangence et répond à la vitesse
entrante aux points de contact. Si une sphère commence à l'intérieur d'une
boîte, la normale de réponse peut être opposée à celle de la requête
`Geometry3D.distance`, afin de l'expulser par la face la plus proche.

Chaque corps choisit `friction` (0,6 par défaut) et `restitution` (0 par
défaut) dans `RigidBody3DSettings` ou avec `set_material`. La friction doit
être finie et positive ou nulle ; la restitution doit être finie dans
`[0, 1]`. Pour une paire, le monde utilise la moyenne géométrique des
frictions et la plus grande restitution. Un choc de vitesse normale
supérieure à 1 reçoit la restitution ; les chocs plus lents ne rebondissent
pas. L'impulsion tangentielle reste bornée par la friction combinée fois
l'impulsion normale. `Contact3D.friction()`, `restitution()` et
`tangent_impulse()` exposent ces résultats du pas.

La détection examine actuellement chaque paire de corps actifs dont au moins
un est dynamique. Une séparation positive inférieure à `10⁻⁶` peut conserver
une paire au repos malgré l'arrondi numérique ; les requêtes autonomes gardent
la séparation mesurée. Pour deux boîtes, elle découpe la face incidente contre
les bords de la face de référence, écarte les points au-dessus de celle-ci et
garde jusqu'à quatre appuis répartis. Ce travail borné est effectué pour
chaque paire de boîtes en contact à chaque pas. Les impulsions des points
proches sont reprises au pas suivant tant que les mêmes handles et
la même orientation de contact subsistent. Deux capsules presque parallèles
peuvent conserver deux points latéraux ; les autres configurations gardent
un seul point. Un petit empilement et des boîtes initialement inclinées sur un
sol plat se stabilisent au pas fixe testé. Les contacts arête contre arête et
les appuis glissants peuvent encore dériver ; le CCD linéaire reste optionnel
et la friction statique n'est pas garantie. `step(0)` conserve les dernières observations ;
détruire un corps retire les contacts courants qui le citent. Un snapshot
conservé garde ses mesures, mais ses handles deviennent invalides avec leurs
corps ou leur monde.

## Début et fin des contacts

Après chaque pas positif, `write_contact_begin_events(output)` et
`write_contact_end_events(output)` copient des snapshots `Contact3D` dans des
tableaux fournis par le consommateur. Le début est émis une fois pour une
nouvelle paire de corps et sous-formes ; la persistance n'émet ni nouveau
début ni fin. La fin est émise au premier pas positif où la paire disparaît.
Une paire qui change d'enfant dans un composé produit une fin pour l'ancien
ID et un début pour le nouveau.

La destruction retire immédiatement le contact courant et programme sa fin
pour le prochain pas positif ; la désactivation ou l'éloignement sont constatés
à ce pas. `step(0)` conserve les événements du dernier pas et les fins encore
en attente. Les snapshots copiés gardent point, normale, séparation et ID
d'enfant après les pas suivants. Leurs handles permettent toujours
`is_valid()` et `same_body()` ; les lectures d'état d'un corps détruit restent
invalides. `same_body(other)` emprunte l’autre poignée en lecture : la
comparaison accepte aussi une poignée atteinte depuis un état emprunté, sans
en conserver une copie. Le recyclage d’un emplacement ne confond pas l’ancien
et le nouveau corps. Un corps endormi peut garder un contact et n'émet pas de fin pour le
seul motif du sommeil.

## Propriété et durée de vie

Chaque monde possède son stockage et ses corps. `RigidBody3D` est un handle
typé avec une génération : détruire un corps invalide toutes ses copies,
même si son emplacement est réutilisé. La fin du monde invalide également
les handles conservés, sans que ceux-ci maintiennent le monde vivant.
`is_valid()` permet de les vérifier ; toute autre lecture d'un handle périmé
échoue explicitement. Un monde refuse de détruire le corps d'un autre monde.
`write_bodies` remplit un tableau fourni par le consommateur avec les corps
vivants, sans promettre un ordre de création.

Le monde fournit les requêtes spatiales et le CCD linéaire décrits ci-dessus.
Les [requêtes géométriques autonomes](Geometry3D.md) restent disponibles
pour les formes isolées ; leur politique bilatérale reste distincte de la
réponse unilatérale du terrain.

Les cylindres et formes effilées décrits dans [la géométrie autonome](Geometry3D.md#cylindres-et-formes-effilées)
emploient leur centre de masse géométrique et un tenseur axial exact. Le CCD
translationnel accepte leurs surfaces rondes ; un choc sur un bord peut laisser
une vitesse du centre et produire une rotation, tout en annulant la vitesse
normale au point de contact. L’orientation balayée reste celle du début du pas.

Les [plans](Geometry3D.md#plan-et-demi-espace) fixes occupent leur demi-espace
négatif. Un corps discret qui traverse la surface reste recouvrant et est
corrigé ; contrairement à un mur mince, il ne trouve pas une extrémité libre
de l'autre côté. Le CCD place le premier impact avec l'orientation initiale.
Les plans actifs sont sélectionnés explicitement, indépendamment des bornes
finies des autres corps, y compris dans les requêtes de personnage.

### Ce que le CCD garantit en rotation

Le balayage conserve l'orientation initiale des deux formes. La rotation est
intégrée pendant le pas, mais aucune enveloppe de la trajectoire angulaire
n'est balayée. Une rotation seule, ou accompagnée d'une translation parallèle
à un obstacle, peut donc le traverser entre deux configurations séparées.
L'option `continuous_collision` ne constitue pas un CCD rotationnel exact.

Le cas qualifié utilise une lame de dimensions `(0.1, 2, 0.1)`, centrée en
`(-0.4, 0, 0)`, contre un mur fixe de dimensions `(0.1, 4, 4)` à l'origine.
Elle tourne de 180° autour de Z en `1/60` seconde. À 90°, elle recouvre le mur ;
aux deux extrémités du pas, elle est séparée. Silex et Jolt épinglé manquent
ce contact avec un seul pas, y compris avec une translation parallèle de
120 unités/s sur Z. Les 36 pas de `1/2160` seconde trouvent un contact dans
les deux cas. Gravité, amortissements et friction sont nuls ; la limite de
vitesse angulaire Jolt est portée à 1000 rad/s pour préserver la vitesse demandée.

Réduire le pas permet de détecter ces cas, mais un nombre fixe de sous-pas
n'offre pas une garantie universelle en rotation. La qualification compare
l'absence puis la présence d'un contact ; les trajectoires après impact ne
sont pas déclarées identiques entre moteurs. Choisir le pas selon la vitesse
angulaire, la distance balayée et l'épaisseur des obstacles.
