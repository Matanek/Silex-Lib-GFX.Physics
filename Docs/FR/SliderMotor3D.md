# Moteur de glissière 3D

`SliderMotor3D(speed, maximum_force)` entraîne un chariot à une vitesse
relative signée, avec une capacité de force symétrique. La vitesse est en
m/s sur l'axe X du premier repère ; la capacité est en N. Le rail peut
se déplacer et tourner. Le moteur préserve les cinq mouvements bloqués
par la [glissière](Slider3D.md).

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0)
        ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings()
        ..motor = Physics.SliderMotor3D(0.6, 2.0))
    var step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.6) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D(0.0, 2.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001)
    joint.set_motor(null)
    assert(joint.motor() == null && joint.motor_force() == 0.0)
}
```

`speed` est fini ; `maximum_force` est fini et positif ou nul. La capacité
borne la force moteur cumulée pendant un pas, quelle que soit la quantité
d'itérations. Le moteur accélère progressivement vers sa cible : une charge
supérieure à sa capacité peut empêcher la vitesse demandée, voire faire
reculer le chariot. Une capacité nulle n'entraîne ni ne freine l'axe.

`SliderConstraint3DSettings.motor` est facultatif. `null` laisse la course
libre ; une vitesse cible nulle freine puis maintient le chariot avec la
même capacité. `joint.motor()` rend une valeur facultative décrivant la
commande courante. `set_motor(motor)` remplace cette commande ; `set_motor(null)`
désactive le pilotage tout en conservant les retenues et butées de la glissière.
Le remplacement efface les réactions et réveille les deux corps.

`motor_force()` donne la force moteur signée en N sur le second repère,
positive vers la course croissante, pendant le dernier pas positif.
`reaction_force()` inclut le moteur, les butées et les retenues transversales.
`limit_force()` reste la seule réaction axiale des butées. Un moteur qui
pousse contre une butée peut donc fournir sa capacité, tandis que la butée
la compense : une réaction totale nulle ne signifie pas que le moteur est libre.
`reaction_torque()` reste le couple libre d'orientation ; il peut compenser
le moment d'une force moteur appliquée à un ancrage excentré.

`step(0.0)` conserve les dernières mesures. Changer les repères, limites
ou activation efface également la mesure moteur. Suspendre un corps ou la
contrainte empêche le pilotage et remet ses efforts à zéro au prochain pas
positif. Une cible non nulle avec capacité positive réveille les corps ;
une cible nulle peut laisser une assemblée immobile dormir. Les règles
de destruction et de références périmées sont celles de la glissière.

Le consommateur et l'oracle Jolt qualifient accélération, inversion, freinage,
deux masses libres, ancrage excentré et charge supérieure à la capacité.
Le rail tournant est comparé en régime établi à vitesse relative constante.
La parité des transitions d'effort pendant une rotation du rail, des impacts
et des chaînes spatiales générales reste à établir. Bornes de force signées,
friction passive et butées souples restent à qualifier.

`SliderMotorScene.sx` commence en montée à −1 m/s sur un rail incliné.
T alterne montée, freinage puis descente ; F choisit 30 ou 6 N, cette dernière
capacité étant insuffisante pour monter. D désactive/réactive le moteur ;
R réinitialise, Espace met en pause/reprend et Échap ferme.

[Le servo de position](SliderPosition3D.md) ajoute une course cible par ressort amorti.
