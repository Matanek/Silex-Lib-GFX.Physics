# Freiner une charnière libre

`maximum_friction_torque` oppose un couple borné à la rotation relative
d’une charnière sans moteur. Le frein ralentit le mouvement jusqu’au repos ;
il peut retenir une charge qui reste sous sa capacité. Zéro laisse l’axe libre.

## Ralentir, relâcher puis motoriser

Cette roue sans gravité démarre à 1 rad/s avec une inertie de 0,1 kg·m².
Un couple de friction de 0,1 N·m l’arrête en une seconde. Le programme
relâche ensuite le frein, installe un moteur puis rend la main à la friction.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) { var i = 0; while i < count { world.step(1.0/60.0); i++ } }
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var wheel = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,wheel,
        Physics.HingeConstraint3DSettings() ..maximum_friction_torque = 0.1)
    wheel.set_angular_velocity(Math.Vec3(0.0,0.0,1.0)); steps(world,90)
    assert(Math.abs(hinge.angular_speed())<0.00001)
    hinge.set_maximum_friction_torque(0.0)
    wheel.set_angular_velocity(Math.Vec3(0.0,0.0,-1.0)); steps(world,30)
    assert(Math.abs(hinge.angular_speed()+1.0)<0.00001 && hinge.friction_torque()==0.0)
    hinge.set_maximum_friction_torque(0.2)
    hinge.set_motor(Physics.HingeMotor3D(0.5,1.0)); steps(world,60)
    assert(Math.abs(hinge.angular_speed()-0.5)<0.00001 && hinge.friction_torque()==0.0)
    hinge.set_motor(null); steps(world,60)
    assert(Math.abs(hinge.angular_speed())<0.00001 && hinge.motor_torque()==0.0)
}
```

`HingeConstraint3DSettings.maximum_friction_torque` configure le frein à la
création. `set_maximum_friction_torque(torque)` le règle pendant la simulation ;
`maximum_friction_torque()` retrouve sa capacité configurée. Le couple est
en N·m, fini et positif ou nul. Une valeur négative ou non finie est rejetée.

## Choisir entre frein et moteur

La friction est passive : elle agit quand `hinge.motor() == null`. Un moteur
installé prend la main, qu’il vise une vitesse ou un angle, même avec un
couple maximal nul. La capacité de friction reste mémorisée ; `set_motor(null)`
la réactive. Pour laisser l’axe libre sans moteur, régler cette capacité à zéro.

Le frein applique au plus sa capacité de couple sur chaque pas ; son effort
réduit la vitesse relative sans imposer un retour vers un angle initial.
Il fournit aussi la réaction nécessaire à une charge immobile sous sa capacité.
Une charge supérieure le fait glisser. Ce n’est pas un amortissement visqueux
proportionnel à la vitesse, ni un verrou d’angle.

## Mesurer et modifier

`friction_torque()` mesure le couple signé appliqué au second corps au dernier
pas positif ; le premier reçoit l’opposé. Sa valeur reste bornée par la
capacité configurée et vaut zéro quand un moteur prend la main.
`motor_torque()` reste réservé à l’effort du moteur. `reaction_torque()`
inclut la friction, les réactions d’axe et de butée.

Une mutation de capacité réveille les corps et efface les réactions, comme
les autres mutations de charnière. Un pas nul conserve les mesures. La
friction passive permet le sommeil au repos ; désactiver un corps ou la
charnière suspend son effort. Les handles périmés et orphelins suivent les
[gardes de charnière](Hinge3D.md).

Le pivot excentré, la masse, le centre de masse et l’inertie déterminent la
réponse du mécanisme. Friction, contacts et autres contraintes partagent le
même monde. Voir le [pilotage en position](HingePosition3D.md) pour viser un
angle et la [charnière](Hinge3D.md) pour ses repères et butées.
