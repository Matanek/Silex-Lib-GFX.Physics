# Inclinaison et torsion 3D

`World3D.create_swing_twist_constraint` garde deux attaches ensemble, borne
leur torsion (twist) autour de X et leur inclinaison (swing) autour de Y/Z.
Les deux commandes peuvent être activées séparément.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var support=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type=Physics.BodyType3D.fixed ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var body=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep=false ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var joint=world.create_swing_twist_constraint(support,body,
        Physics.SwingTwistConstraint3DSettings() ..swing_limits=Physics.SwingLimits3D.cone(Math.Vec2(0.3,0.6))
        ..minimum_twist=-0.4 ..maximum_twist=0.4
        ..twist_motor=Physics.TwistMotor3D.position(0.2,5.0,2.0,1.0))
    var i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.twist_angle()-0.2)<0.002 && joint.anchor_error().length()<0.001)
    joint.set_twist_motor(null)
    joint.set_swing_motor(Physics.SwingMotor3D.position(Math.Vec2(0.2,0.0),5.0,2.0,1.0))
    i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.swing_angles().x-0.2)<0.002)
    world.destroy_swing_twist_constraint(joint);assert(!joint.is_valid())
    print("swing twist recipe: ok")
}
```

## Repères et limites

`first_local_frame` et `second_local_frame` sont locaux au repère de forme de
chaque corps. Leur origine est l’ancrage ; leur rotation définit X pour la
torsion et Y/Z pour l’inclinaison. `orientation()` est la rotation du second
repère par rapport au premier. Elle se décompose en swing puis twist.
`twist_angle()` est signé dans [−π, π]. `swing_angles()` contient les angles
Y/Z `2 atan2(q.y, q.w)` et `2 atan2(q.z, q.w)` du quaternion swing : ce ne
sont pas des angles d’Euler. À 180° d’inclinaison, la torsion devient singulière ;
le témoin de décomposition choisit alors un twist nul.

`SwingLimits3D.cone(half_angles)` borne le swing par une ellipse du plan
quaternion Y/Z, de rayons `sin(half_angles.x/2)` et `sin(half_angles.y/2)`.
Les demi-angles appartiennent à [0, π] ; zéro verrouille une direction,
π la libère. `pyramid(minimum, maximum)` borne les deux angles swing par
un rectangle. Les bornes finies appartiennent à [−π, π] et contiennent
l’orientation neutre zéro ; elles peuvent être asymétriques. Pour déplacer
cette orientation neutre, tourner les repères locaux. Les limites de twist
sont finies et ordonnées dans [−π, π], égales pour verrouiller la torsion.
Par défaut toutes les rotations sont libres.

## Commandes et friction

`TwistMotor3D(speed, maximum_torque)` et `SwingMotor3D(speed, maximum_torque)`
commandent respectivement une vitesse angulaire scalaire ou Y/Z, en rad/s.
Ces composantes sont portées par le second repère de contrainte. Pour des
rotations combinées, elles ne sont pas les dérivées des angles swing affichés.
Les surcharges `minimum_torque, maximum_torque` donnent des bornes signées
en N·m. Le budget swing s’applique indépendamment à Y et Z.

Les fabriques `position` et `position_and_velocity` ajoutent une cible angulaire
en radians, une raideur en N·m/rad et un amortissement en N·m·s/rad.
La cible est projetée sur les limites admissibles : projection euclidienne
sur l’ellipse quaternion pour le cône. Une partie sans servo conserve son
orientation courante lors du calcul de la cible composée. Les erreurs de servo
utilisent le quaternion le plus proche, avec l’approximation angulaire `2 sin(θ/2)`.

`maximum_friction_torque` freine chaque direction non motorisée sans injecter
d’énergie. Un moteur présent avec un budget nul remplace cette friction sur
sa direction ; `null` rétablit le fonctionnement passif. La friction et les
budgets moteurs sont nuls par défaut.

## Observations, mutation et durée de vie

`angular_speed()` exprime la vitesse relative dans le second repère courant.
`motor_torque()` et `friction_torque()` sont les composantes X/Y/Z dans les
axes moteurs du dernier pas positif. `reaction_force()` et `reaction_torque()`
sont la force en N et le couple libre en N·m sur le second corps dans le monde ;
le couple exclut le moment de la force d’ancrage. `anchor_error()` va du
premier ancrage au second, en mètres. Un pas nul conserve les réactions.

`set_frames`, `set_anchors`, `set_swing_limits`, `set_twist_limits`, les deux
`set_*_motor`, `set_maximum_friction_torque` et `set_enabled` effacent les
réactions et réveillent les corps liés. Désactiver un corps ou l’articulation
suspend la résolution. Deux corps distincts du même monde, dont au moins
un dynamique, sont requis. Destruction explicite, destruction d’un corps ou
du monde invalident le handle ; seul `is_valid()` peut encore lire un handle périmé.

## Qualification

Consommateurs sans rendu : mouvements libres, limites Y/Z/twist, ellipse
diagonale, pyramide asymétrique, axes verrouillés, servos à 60/120 Hz par
récurrence indépendante, friction, budgets signés, changements de repères,
sommeil, contacts et durée de vie. Le témoin Jolt épinglé compare des cas
réduits en Debug/Release. Les chaînes spatiales générales, les servos excentrés
sous charge et l’égalité exacte des réactions au pas d’impact restent à qualifier.
