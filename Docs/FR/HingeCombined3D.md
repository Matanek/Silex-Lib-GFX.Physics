# Suivre ensemble un angle et une vitesse

`HingeMotor3D.position_and_velocity(angle, speed, maximum_torque, stiffness, damping)`
donne au servo une cible d’angle et une vitesse de commande. Pour suivre une
trajectoire, actualiser ces deux valeurs à chaque pas. La forme à six arguments
remplace la capacité symétrique par `minimum_torque, maximum_torque`.

## Suivre une rotation régulière

Le corps commence à 0,5 rad/s ; la cible avance à cette même vitesse. Le
moteur conserve cette poursuite sans couple extérieur ni retard d’amortissement.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..angular_velocity = Math.Vec3(0.0,0.0,0.5)
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,body)
    let dt = 1.0/60.0
    var i = 0
    while i<180 {
        let angle = i as float*dt*0.5
        hinge.set_motor(Physics.HingeMotor3D.position_and_velocity(angle,0.5,-1.0,1.0,1.6,0.8))
        world.step(dt)
        assert(Math.abs(hinge.angle()-(angle+dt*0.5))<0.00001)
        assert(Math.abs(hinge.angular_speed()-0.5)<0.00001)
        assert(Math.abs(hinge.motor_torque())<0.00001)
        i++
    }
    assert(hinge.motor()!.speed==0.5 && hinge.motor()!.target_angle!=null)
}
```

L’angle fourni est celui de la trajectoire au début du pas. Le corps rejoint
l’angle du pas suivant. Une application doit actualiser elle-même la trajectoire :
le moteur ne fait pas avancer automatiquement `target_angle`.

## Choisir les cibles et l’effort

`angle` est fini dans `[-pi, pi]`, `speed` est fini en rad/s. Le signe suit
`hinge.angle()` et `angular_speed()` ; l’erreur d’angle prend le chemin court.
La cible d’angle effective est bornée par les limites actuelles ; l’instantané
conserve l’angle demandé. La vitesse n’est pas bornée par ces limites : une
butée peut fournir le couple qui s’oppose au moteur.

Raideur et amortissement gardent les unités du [servo de position](HingePosition3D.md).
Les [bornes de couple signées](HingeTorqueBounds3D.md) portent sur le couple
moteur total du pas, partagé par toutes les passes. Zéro dans la forme symétrique
laisse l’axe libre. Une vitesse nulle reproduit exactement le mode position.

Le mode combiné ajoute la vitesse au biais du ressort implicite. Avec un angle
fixe et une vitesse non nulle, le corps finit donc décalé de la cible, sans
tourner indéfiniment. Sans charge et hors butée, à pas constant h, raideur k
et amortissement c, l’écart d’équilibre vaut `(c+h*k)*speed/k`. Cette expression
inclut la discrétisation ; les contacts et charges changent l’équilibre.
Pour maintenir précisément un angle fixe, choisir une vitesse nulle.

## Remplacer et observer

`set_motor` remplace les deux cibles, coefficients et bornes, réveille les
corps et efface les réactions. `motor()` conserve `target_angle`, `speed`,
`stiffness`, `damping` et les deux bornes immuables. `position` fournit
toujours une vitesse nulle ; le constructeur de vitesse conserve un angle absent.

`motor_torque()` mesure le couple signé appliqué au second corps au dernier
pas ; le premier reçoit l’opposé. `reaction_torque()` inclut les axes et les
butées ; `limit_torque()` permet de mesurer ces dernières séparément.
Un pas nul conserve ces mesures. Changer de mode ou retirer le moteur suit
les règles de la [charnière](Hinge3D.md). Un moteur installé, même sans effort,
prend la priorité sur la [friction passive](HingeFriction3D.md).

Les [butées souples](HingeSoftLimits3D.md) peuvent se déformer sous la commande
combinée. Mutation de masse, centre de masse, ancrages et repères conserve les
unités physiques ; elle peut changer la poursuite transitoire.
La qualification compare Jolt Debug/Release sur cibles fixes et mobiles,
saturation signée, modes, charges sur butées rigides, pivot excentré, couture
angulaire et inerties différentes. Les impacts rigides ont une différence
d’activation avant/après déplacement ; aucune parité de leur transitoire n’est
revendiquée. Les contacts et la chaîne chargée sont qualifiés dans leur plan ;
les chaînes spatiales générales restent à étendre.
