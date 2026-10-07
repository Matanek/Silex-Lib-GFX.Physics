# Piloter une charnière vers un angle

`HingeMotor3D.position(angle, maximum_torque, stiffness, damping)` approche
un angle signé par un ressort amorti. La charnière conserve son ancrage et
son axe ; son moteur fournit un couple borné. Le constructeur
`HingeMotor3D(speed, maximum_torque)` conserve le pilotage en vitesse.

## Atteindre puis changer la cible

Cette recette utilise un pivot fixe, un corps libre sans gravité et un servo
amorti. Elle inverse ensuite la cible, passe en vitesse puis laisse tourner
le corps avec le moteur absent.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) {
    var index = 0; while index < count { world.step(1.0/60.0); index++ }
}
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,body,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D.position(0.75,10.0,1.6,0.8))
    steps(world,180)
    assert(Math.abs(hinge.angle()-0.75) < 0.001)
    hinge.set_motor(Physics.HingeMotor3D.position(-0.75,10.0,1.6,0.8))
    assert(hinge.motor_torque()==0.0)
    steps(world,180)
    assert(Math.abs(hinge.angle()+0.75) < 0.001)
    hinge.set_motor(Physics.HingeMotor3D(0.5,1.0))
    steps(world,30)
    assert(Math.abs(hinge.angular_speed()-0.5) < 0.00001)
    hinge.set_motor(null)
    steps(world,30)
    assert(Math.abs(hinge.angular_speed()-0.5) < 0.00001)
}
```

`angle` est en radians, dans `[-pi, pi]`, avec le signe de `hinge.angle()`.
Le moteur choisit le chemin angulaire court. Les limites actuelles bornent la
cible effective ; `motor.target_angle` conserve l’angle demandé. Modifier les
limites réévalue donc la cible, sans devoir réinstaller le moteur.

## Régler l’effort et la réponse

Dans la forme symétrique, `maximum_torque` est une valeur finie positive ou nulle, en N·m. La borne
porte sur le couple moteur cumulé du pas. Zéro laisse l’axe libre, comme un
moteur absent ; ce n’est pas un frein rigide.

`stiffness` est une raideur finie strictement positive, en N·m/rad ;
`damping` un amortissement fini positif ou nul, en N·m·s/rad. Une faible
valeur d’amortissement permet des oscillations et dépassements de cible.
Le couple suit le ressort implicite ; aucun déplacement rigide ne projette
l’angle directement sur la cible. À pas fini, l’intégration ajoute un
amortissement numérique, même avec `damping:0.0`.

Sous une charge constante, le servo peut rester décalé de sa cible : son
ressort équilibre le couple extérieur. Une borne de couple trop faible peut
empêcher de rejoindre cet équilibre. La raideur et l’amortissement explicites
conservent leurs unités lorsque l’inertie, la masse ou l’ancrage changent.

L’instantané `hinge.motor()` distingue le mode position par `target_angle`
présent ; il porte aussi `stiffness` et `damping`. En mode vitesse, cet angle
est absent et ces coefficients valent zéro ; `speed` reste la cible signée.
En mode position, `speed` vaut zéro.

## Modifier et observer

`set_motor` remplace l’intention entière, réveille les corps et remet les
réactions à zéro. Il permet de changer cible, coefficients, borne ou mode.
`null` coupe le moteur ; les ancrages, axes et butées restent actifs.
`motor_torque()` mesure le couple moteur signé appliqué au second corps
pendant le dernier pas ; le premier reçoit l’opposé. `reaction_torque()`
inclut aussi les réactions d’axe et de butée. Un pas nul conserve ces mesures.
Les handles périmés ou orphelins suivent les gardes de la
[charnière](Hinge3D.md).

Une butée rigide unilatérale arrête les vitesses qui la franchissent ; une pénétration
existante est corrigée en pose. Resserrement de limites et servo partagent
le monde réel, ses contacts et sa sûreté ; la récupération de pose ne fournit
pas un nouvel élan au corps.

Le [frein d’axe](HingeFriction3D.md) agit quand le moteur est absent. Les
[bornes signées](HingeTorqueBounds3D.md) permettent un effort différent dans chaque sens. Les butées souples restent à compléter. Pour le pilotage en vitesse, voir le [moteur de charnière](Hinge3D.md#viser-une-vitesse-avec-un-couple-maximal).
