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

## Lire les réactions et gérer la durée de vie

`reaction_force()` donne la force mondiale appliquée au second corps au point
d'attache pendant le dernier pas positif. `reaction_torque()` donne le couple
mondial angulaire appliqué au second corps pour aligner les axes et respecter
les butées. Il n'inclut pas le moment de la force d'ancrage autour du centre de
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
Les moteurs, la friction angulaire et les butées souples restent à implémenter.
