# Articuler deux corps autour d'un axe

`World3D.create_hinge_constraint` maintient deux points d'attache et aligne
leurs axes, tout en laissant les corps tourner autour de cet axe. Des butées
rigides bornent cette rotation. La charnière participe aux contacts et aux
îlots de sommeil du [monde 3D](World3D.md).

Ce pendule tourne dans le plan XY et reste attaché à son support fixe :

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.1)))
    let rotation = Math.Quat.angle_axis(0.4,Math.Vec3(0.0,0.0,1.0))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.25))
        ..transform = Physics.Transform3D(rotation.rotate(Math.Vec3(0.0,-1.0,0.0)),rotation)
        ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,weight,Physics.HingeConstraint3DSettings()
        ..second_local_anchor = Math.Vec3(0.0,1.0,0.0)
        ..minimum_angle = -0.5 ..maximum_angle = 0.5)
    var step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(hinge.anchor_error().length() < 0.005)
    assert(hinge.axis_error() < 0.001)
    print("Pendulum angle: $(hinge.angle()) rad")
}
```

## Définir l'axe et l'angle zéro

Les ancrages sont des points dans les repères locaux des corps, indépendants de
leur centre de masse. `first_local_axis` et `second_local_axis` définissent
l'axe de rotation ; ils valent Z par défaut. `first_local_normal` et
`second_local_normal` définissent la direction correspondant à l'angle zéro ;
ils valent X par défaut. Chaque normale doit être indépendante de son axe.
La création normalise l'axe et projette la normale dans son plan perpendiculaire.
Les vecteurs et leurs normes au carré doivent être finis, non nuls et ne pas
être presque colinéaires.

`angle()` mesure la rotation signée du second repère par rapport au premier,
selon la règle de la main droite autour du premier axe, dans `[-pi, pi]`.
`axis_error()` mesure en radians l'écart entre les deux axes ; `anchor_error()`
est le vecteur du premier ancrage mondial vers le second. L'angle est utile
lorsque les axes sont alignés ; corriger une pose initiale fortement désalignée
peut demander plusieurs pas. Pour une rotation initiale considérée comme zéro,
exprimer les deux normales locales afin qu'elles coïncident dans le monde.

## Modifier les butées et les repères

`minimum_angle` et `maximum_angle` sont des radians finis, ordonnés dans
`[-pi, pi]`. Les valeurs par défaut désactivent les butées ; deux valeurs
égales verrouillent l'angle. Les butées sont rigides, sans rebond imposé ni
friction sur l'axe libre. Elles sont résolues à chaque pas de simulation ;
elles ne constituent pas une détection continue de toutes les rotations.

`set_limits(minimum, maximum)`, `set_anchors(first, second)` et
`set_frames(first_axis, first_normal, second_axis, second_normal)` modifient
la charnière vivante. `set_enabled(false)` suspend ses réactions sans détruire
son handle ; `set_enabled(true)` la réactive. Toute mutation réveille les
corps liés et efface les réactions mémorisées.

## Viser une vitesse avec un couple maximal

`HingeMotor3D(speed, maximum_torque)` décrit une vitesse relative en rad/s et
un plafond symétrique de couple. `settings.motor` le configure à la création ;
`set_motor(...)` le remplace à l’exécution. Cet exemple atteint la cible,
inverse le mouvement, puis arrête le moteur :

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var wheel = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,wheel,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D(speed:1.0,maximum_torque:0.2))
    var step = 0
    while step < 60 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(hinge.angular_speed()-1.0) < 0.0001)
    hinge.set_motor(Physics.HingeMotor3D(speed:-1.0,maximum_torque:0.2))
    step = 0
    while step < 90 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(hinge.angular_speed()+1.0) < 0.0001)
    hinge.set_motor(null)
    assert(hinge.motor() == null && hinge.motor_torque() == 0.0)
    print("Hinge motor: target, reversal and off verified")
}
```

`speed` suit le signe de `angle()` ; `angular_speed()` mesure la vitesse du
second corps par rapport au premier, projetée sur le premier axe mondial.
Les deux paramètres sont finis et `maximum_torque` doit être positif ou nul.
Un couple nul ne fournit aucun effort. Une cible nulle freine la rotation,
alors que `set_motor(null)` laisse l’axe libre et conserve sa vitesse actuelle.
`motor()` retourne la configuration optionnelle courante. Une copie de cette
valeur est indépendante des mutations ultérieures de la charnière.

`motor_torque()` mesure le couple signé du moteur pendant le dernier pas
positif, en N·m avec kilogrammes, mètres et secondes. Il reste borné par le
plafond, indépendamment du nombre d’itérations ou de la durée du pas.
Les réactions d’ancrage et de butée peuvent dépasser ce plafond : il limite
l’effort du moteur. Une butée peut donc arrêter le corps malgré la cible ;
le moteur continue à pousser et sa réaction de butée peut annuler son couple.
La cible demande un effort disponible, sans garantir qu’elle sera atteinte
sous une charge trop forte.

Une mutation efface les observations et réveille les corps liés. Un moteur
actif à vitesse non nulle et couple disponible garde ses corps éveillés ;
une cible nulle peut les laisser dormir une fois arrêtés. Désactiver la
charnière ou un corps suspend le moteur. `step(0)` conserve son observation.
Les charnières actives, y compris passives, sont préparées après les forces
et avant le déplacement, puis résolues avec les contacts ; le plafond
d’effort est partagé entre ces phases.

## Lire les réactions et gérer la durée de vie

`reaction_force()` donne la force mondiale appliquée au second corps au point
d'attache pendant le dernier pas positif. `reaction_torque()` donne le couple
mondial angulaire appliqué au second corps par le moteur, l’alignement des axes
et les butées. Il n'inclut pas le moment de la force d'ancrage autour du centre de
masse. Les unités sont masse × distance / seconde² et masse × distance² /
seconde² ; avec kilogrammes, mètres et secondes, ce sont des newtons et N·m.
`step(0)` conserve les observations ; une charnière inactive donne une réaction
nulle après le pas positif suivant, ou dès sa désactivation explicite.

Les deux corps doivent être distincts, vivants et appartenir au même monde ;
au moins un doit être dynamique. Les collisions entre eux restent actives.
Utiliser les filtres des corps si leurs formes se chevauchent autour du pivot.
Désactiver un corps suspend aussi la résolution de ses charnières.

`destroy_hinge_constraint(hinge)` invalide toutes les copies du handle.
Détruire un corps lié ou le monde les invalide aussi ; `is_valid()` permet le
contrôle. `first_body()` et `second_body()` retrouvent les corps liés, et
`hinge_constraint_count()` compte uniquement les charnières vivantes.

La qualification couvre des pendules, des butées mutées, une chaîne à masses
asymétriques et des contacts terrain sur macOS ARM64 Native Debug/Release.
Le moteur à vitesse cible est qualifié par accélération analytique, inertie au
pivot, inversion, arrêt, butées, chaîne et contacts. Le
[pilotage en position](HingePosition3D.md) et la
[friction d’axe](HingeFriction3D.md) sont disponibles. Les [butées souples](HingeSoftLimits3D.md) sont disponibles avec raideur et
amortissement physiques.

Les [bornes de couple signées](HingeTorqueBounds3D.md) permettent un effort différent dans chaque sens, en vitesse ou en position.

La [commande combinée](HingeCombined3D.md) suit un angle et une vitesse actualisés ensemble.

## Porter une charge hors du plan

Une charnière peut porter une charge déportée par une attache fixe. La
qualification couvre un déport de ±1 m sous gravité, une charge de 2 kg,
l’inversion d’un moteur plafonné à 0,2 N·m, un sol présent ou retiré et des
pas à 60/120 Hz. Les ancrages restent sous 0,01 m pendant ces parcours ;
l’erreur d’axe descend sous 0,002 rad après convergence. Le cas sans gravité
vérifie aussi l’inertie complète de l’assemblage autour du pivot.

Le plafond moteur reste partagé sur tout le pas, même lorsque sa durée
change. Une mutation de charnière efface ses efforts précédents. Une
réactivation après déplacement libre peut demander plusieurs pas pour
retrouver les ancrages, comme une correction de pose initiale. Si un corps
est déplacé dans la zone libre d’une butée souple, l’effort de cette ancienne
butée cesse au prochain pas positif.

Les positions, vitesses et réactions sont comparées à Jolt après 2,5 s sur
des parcours de 3 s. Les trajectoires initiales et les phases de contact
diffèrent ; ces preuves ne garantissent pas une chaîne quelconque, une
charge arbitraire ou une correction identique dès le premier pas.
