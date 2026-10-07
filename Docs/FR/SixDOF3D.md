# Attache à six degrés de liberté

`World3D.create_six_dof_constraint` configure séparément les translations
X/Y/Z et les rotations d’une attache. Tous les degrés sont libres par défaut.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var support=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type=Physics.BodyType3D.fixed ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var body=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep=false ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    let locked=Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.locked
    let travel=Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.bounded(-0.3,0.3)
        ..motor=Physics.LinearMotor3D.position(0.2,100.0,20.0,8.0)
    var joint=world.create_six_dof_constraint(support,body,Physics.SixDOFConstraint3DSettings()
        ..translation_x=travel ..translation_y=locked ..translation_z=locked
        ..swing_limits=Physics.SwingLimits3D.cone(Math.Vec2())
        ..minimum_twist=-0.4 ..maximum_twist=0.4
        ..rotation_x_motor=Physics.AngularMotor3D.position(0.1,10.0,2.0,1.0))
    var i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.translation().x-0.2)<0.002 && Math.abs(joint.twist_angle()-0.1)<0.002)
    joint.set_rotation_x_motor(null)
    joint.set_translation_x(Physics.LinearAxis3DSettings() ..limit=Physics.LinearLimit3D.bounded(-0.3,0.3)
        ..motor=Physics.LinearMotor3D.position(-0.15,100.0,20.0,8.0))
    assert(joint.motor_force().length()==0.0 && joint.motor_torque().length()==0.0)
    i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.translation().x+0.15)<0.002)
    world.destroy_six_dof_constraint(joint);assert(!joint.is_valid())
    print("six DOF recipe: ok")
}
```

## Translations et repères

Les origines et rotations de `first_local_frame` et `second_local_frame` sont
locales aux repères de forme des corps, comme pour swing/twist. Les translations
suivent les axes du premier repère. `translation()` est le déplacement du
second ancrage par rapport au premier dans ce repère, en mètres.
`translation_speed()` en est la dérivée en m/s, y compris lorsque le premier
repère tourne. `anchor_error()` est ce déplacement dans le monde ; une valeur
non nulle est admissible lorsqu’un degré est libre ou borné hors zéro.

`translation_x`, `translation_y` et `translation_z` contiennent chacun un
`LinearAxis3DSettings`. `LinearLimit3D.free` libère le mouvement ; `locked`
retient la coordonnée zéro ; `bounded(minimum, maximum)` donne une plage
finie strictement ordonnée en mètres. Déplacer l’origine d’un repère pour
verrouiller une autre coordonnée de référence.

`limit_spring=LinearLimitSpring3D(stiffness, damping)` rend une limite
verrouillée ou bornée élastique : raideur positive en N/m, amortissement
non négatif en N·s/m. Une butée élastique autorise la compression sous charge
et ne corrige pas directement la position. Son effort n’est pas limité par
le budget d’un moteur ; sous charge constante F, sa compression au repos est F/k.
Un ressort associé à un degré libre est rejeté.

## Rotations et moteurs

Le twist autour de X est borné par `minimum_twist` et `maximum_twist` en
radians. `swing_limits` définit un cône elliptique ou une pyramide pour Y/Z.
La [géométrie swing/twist](SwingTwist3D.md) décrit les angles, leur singularité
à 180° et les repères. Une pyramide peut exclure zéro ; des bornes égales
verrouillent un angle, y compris non nul.

Chaque translation accepte un `LinearMotor3D` : vitesse en m/s, bornes de
force en N, cible en mètres, raideur en N/m et amortissement en N·s/m.
`rotation_x_motor`, `rotation_y_motor` et `rotation_z_motor` acceptent chacun
un `AngularMotor3D` : vitesse en rad/s, couple en N·m, cible en radians,
raideur en N·m/rad et amortissement en N·m·s/rad. Les directions angulaires
sont portées par le second repère. Les cibles Y/Z sont les coordonnées swing,
et leurs vitesses commandées ne sont pas les dérivées de ces coordonnées
lors de rotations combinées.

Les constructeurs donnent une vitesse et une capacité symétrique, ou des
bornes signées `minimum_force/torque` et `maximum_force/torque`. Les fabriques
`position` et `position_and_velocity` ajoutent une cible et un ressort amorti.
Les cibles sont projetées sur les limites. Les trois commandes ont leurs
budgets et paramètres indépendants ; un servo absent conserve sa partie
courante dans la cible angulaire composée.

`maximum_friction_force` freine une translation non motorisée ;
`maximum_rotation_friction_torque` fournit les capacités X/Y/Z des rotations
non motorisées. Capacités finies non négatives, zéro par défaut. Un moteur
présent à capacité nulle remplace la friction ; `null` la rétablit.

## Réactions et mutation

`reaction_force()` et `reaction_torque()` donnent la force en N et le couple
libre en N·m sur le second corps, dans le monde. Le couple exclut le moment
des forces d’ancrage. `motor_force`, `friction_force` et `limit_force` donnent
les efforts scalaires X/Y/Z des axes linéaires ; `motor_torque` et
`friction_torque` donnent ceux des commandes angulaires. Ces mesures portent
sur le dernier pas positif ; un pas nul les conserve. Pour une direction
globale résultante, employer les réactions globales.

`set_translation_x/y/z` remplace toute la configuration de la direction.
`set_rotation_x/y/z_motor`, `set_maximum_rotation_friction_torque`,
`set_swing_limits`, `set_twist_limits`, `set_frames`, `set_anchors` et
`set_enabled` invalident les réactions et réveillent les corps liés.
La création demande deux corps distincts du même monde, dont au moins un
dynamique. Désactivation du corps ou de l’attache suspend la résolution ;
destruction explicite, destruction d’un corps ou du monde invalide le handle.
Seul `is_valid()` reste utilisable sur un handle périmé.

## Qualification

Consommateurs sans rendu : degrés libres/verrouillés/bornés, commandes
indépendantes et simultanées, friction, butée souple chargée, repères tournés,
masses différentes, ancrage excentré au repos, contacts et durée de vie.
Servos linéaires et angulaires vérifiés par récurrences indépendantes à
60/120 Hz ; témoin Jolt épinglé Debug/Release sur seize cas réduits.
Les chaînes spatiales générales, les servos excentrés chargés et l’égalité
exacte des réactions au pas d’impact restent à qualifier.
