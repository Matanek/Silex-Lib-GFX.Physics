# Piloter avec des couples différents selon le sens

`HingeMotor3D(speed, minimum_torque, maximum_torque)` borne l’effort moteur
entre deux couples signés en N·m. L’exemple accélère vers +1 rad/s avec
0,1 N·m, puis inverse la cible avec seulement −0,025 N·m : la rotation reste
positive pendant le freinage plus lent. Le constructeur à deux arguments
conserve une capacité symétrique dans les deux sens.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) {
    var i = 0; while i < count { world.step(1.0/60.0); i++ }
}
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,body,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D(speed:1.0,minimum_torque:-0.025,maximum_torque:0.1))
    steps(world,60);assert(Math.abs(hinge.angular_speed()-1.0)<0.0001)
    hinge.set_motor(Physics.HingeMotor3D(speed:-1.0,minimum_torque:-0.025,maximum_torque:0.1))
    steps(world,60);assert(Math.abs(hinge.angular_speed()-0.75)<0.0001)
    hinge.set_motor(Physics.HingeMotor3D.position(angle:-0.5,minimum_torque:-0.2,maximum_torque:0.1,
        stiffness:1.6,damping:0.8))
    steps(world,360);assert(Math.abs(hinge.angle()+0.5)<0.02)
    hinge.set_motor(Physics.HingeMotor3D(1.0,0.2))
    assert(hinge.motor()!.minimum_torque == -0.2 && hinge.motor()!.maximum_torque == 0.2)
}
```

Le servo accepte aussi `HingeMotor3D.position(angle, minimum_torque,
maximum_torque, stiffness, damping)`. Il conserve les unités et le ressort
implicite du [pilotage en position](HingePosition3D.md).

## Choisir l’intervalle signé

Le signe suit `angular_speed()` : un couple positif tend à augmenter la
rotation du second corps relative au premier, autour de l’axe du premier.
Le premier reçoit l’effort opposé. Les deux bornes sont finies et ordonnées ;
elles peuvent être égales et zéro n’est pas obligé d’appartenir à l’intervalle.

| Intervalle | Effort permis |
|---|---|
| `[-0.2, 0.2]` | Capacité symétrique |
| `[-0.025, 0.1]` | Effort négatif quatre fois plus faible |
| `[0.0, 0.1]` | Couple positif seulement ; ne peut pas freiner une rotation positive |
| `[0.03, 0.08]` | Effort positif continu, même à la cible |
| `[-0.02, -0.02]` | Couple négatif imposé |
| `[0.0, 0.0]` | Aucun effort moteur |

Une borne de couple n’interdit pas un sens de rotation déjà présent. Avec
une capacité dans un seul sens, le moteur peut ne pas atteindre sa cible.
Un intervalle excluant zéro impose sa borne la plus proche de zéro quand
la commande demanderait moins d’effort, y compris avec une cible nulle.
Prévoir cette action continue avant de choisir de telles bornes.

## Remplacer et mesurer le moteur

`set_motor` remplace cible, bornes et mode ensemble, réveille les corps et
remet les réactions à zéro. L’instantané `motor()` expose `minimum_torque`
et `maximum_torque` comme bornes signées immuables. Les formes symétriques
existantes donnent `minimum_torque == -maximum_torque` ; leur argument de
capacité reste positif ou nul.

`motor_torque()` mesure le couple signé du dernier pas où le moteur agit
sur des corps actifs, dans l’intervalle configuré. Avant le premier pas,
après mutation ou pendant une suspension, la mesure vaut zéro, même si
l’intervalle exclut zéro. La capacité n’est pas multipliée par le nombre d’itérations.
`reaction_torque()` inclut également les axes et butées ; ces dernières
peuvent s’opposer au moteur et arrêter le mouvement. Un pas nul conserve
les observations. Mutation, suspension, destruction et handles orphelins
suivent la [charnière](Hinge3D.md).

Un moteur installé, même sans effort, conserve la priorité sur la
[friction passive](HingeFriction3D.md). `set_motor(null)` le retire. Les
[butées souples](HingeSoftLimits3D.md) sont disponibles ; la commande combinée
position/vitesse reste à qualifier.
