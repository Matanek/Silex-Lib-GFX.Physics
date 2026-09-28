# Simuler des corps rigides en 3D

`World3D` simule des corps fixes, cinématiques et dynamiques sans fenêtre,
scène, renderer ni ECS. Il accepte les sphères, boîtes et capsules de `Shape3D` et
fournit une réponse aux contacts entre ces formes. Les appuis de boîtes sur
des faces presque parallèles utilisent plusieurs points ; un mouvement rapide
peut encore traverser un obstacle.

Un `Compound3D` immuable peut aussi servir de forme à un corps **fixe**. Le
monde teste ses enfants primitifs et expose `Contact3D.first_child_id()` et
`second_child_id()` pour l'enfant retenu ; `-1` désigne une forme primitive.
Le contact retient actuellement l'enfant dont la séparation signée est la
plus petite, avec un seul manifold par paire de corps. Un composé dynamique
ou cinématique est refusé. La masse d'un composé dynamique, les mutations et
les terrains restent à livrer.

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

## Poses, masse et commandes

Le repère suit `STD.Math` : droit, Y vers le haut. `Transform3D.position`
place l'origine de la forme ; `rotation` est un quaternion unitaire. Les
vitesses linéaire et angulaire sont exprimées dans le monde. `world_center_of_mass()`
retourne le centre de masse, qui peut différer de l'origine de la forme.
Les angles et vitesses angulaires sont en radians. `step(delta)` reçoit des
secondes et rejette une durée négative ou non finie.

Par défaut, un corps est dynamique, porte une sphère de rayon 0,5 et reçoit
une densité de 1. La masse et les trois moments d'inertie principaux sont
calculés pour la sphère, la boîte ou la capsule homogène. `MassProperties3D` permet de
fixer une masse positive, un centre local et trois moments locaux positifs ;
les axes principaux coïncident alors avec les axes locaux de la forme.
L'inertie est orientée dans le monde pour les couples et impulsions. Une
impulsion ou force avec un point d'application mondial produit aussi un
moment autour du centre de masse. `apply_torque` et
`apply_angular_impulse` agissent directement sur la rotation.

Un corps fixe garde sa pose et refuse forces et impulsions. Un corps
cinématique avance avec ses vitesses configurées ; `move_kinematic(target,
duration)` calcule des vitesses pour atteindre une pose à une date donnée,
puis les annule. La cible est atteinte exactement si un pas couvre la fin de
la durée. `set_transform`, `set_linear_velocity`,
`set_angular_velocity`, `set_enabled` et `set_mass_properties` permettent les
changements directs. La masse ne peut être remplacée que sur un corps
dynamique.

## Relier deux corps par une distance

`create_distance_constraint(first, second, settings)` relie deux ancrages
locaux appartenant au même monde. `DistanceConstraint3DSettings(longueur)`
impose d'abord une longueur exacte ; ses champs `minimum_length` et
`maximum_length` permettent aussi une plage. Les longueurs sont finies,
positives ou nulles et ordonnées. Au moins un corps doit être dynamique ; un
corps fixe peut servir d'ancrage au monde. Les contraintes actives partagent
les itérations de vitesse avec les contacts et corrigent également leur erreur
de position.

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

`first_local_anchor` et `second_local_anchor` déplacent les points d'attache
dans les repères locaux des corps. `current_length()` mesure leur écart
mondial. `reaction_force()` donne la force exercée sur le second corps pendant
le dernier pas positif, en masse × distance / seconde² ; elle vaut zéro pour
une contrainte inactive ou un pas sans impulsion. `set_limits(minimum, maximum)`
et `set_enabled(enabled)` réveillent les corps liés et effacent la réaction
précédente. `destroy_distance_constraint` invalide le handle ; détruire un
corps lié invalide aussi ses contraintes. `distance_constraint_count()` compte
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

Ces deux familles sont rigides. Ressorts, moteurs et autres articulations
restent à livrer. Un choc très rapide peut encore traverser un obstacle, car
le monde n'a pas de CCD.

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
réveil se propage par contact ou contrainte de distance ou de point au pas suivant. `step(0)` ne modifie ni le
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
les appuis glissants peuvent encore dériver ; il n'y a ni CCD ni garantie de
friction statique. `step(0)` conserve les dernières observations ;
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
invalides. Le recyclage d'un emplacement ne confond pas l'ancien et le nouveau
corps. Un corps endormi peut garder un contact et n'émet pas de fin pour le
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

Le monde ne fournit pas encore de requêtes spatiales intégrées ni de CCD.
Les [requêtes géométriques autonomes](Geometry3D.md)
restent disponibles pour les formes isolées.
