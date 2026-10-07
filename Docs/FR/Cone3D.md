# Articulation cône 3D

`World3D.create_cone_constraint` maintient deux ancrages ensemble et borne
l’inclinaison entre deux axes. Le corps peut tourner librement autour de son
axe et s’incliner librement à l’intérieur du cône.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var support = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var joint = world.create_cone_constraint(support,body,
        Physics.ConeConstraint3DSettings() ..half_angle = 0.4)
    body.set_angular_velocity(Math.Vec3(2.0,0.0,0.0))
    var i = 0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.angle()-0.4)<0.002 && joint.anchor_error().length()<0.001)
    joint.set_half_angle(0.2)
    i = 0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.angle()-0.2)<0.002)
    world.destroy_cone_constraint(joint);assert(!joint.is_valid())
    print("cone recipe: ok")
}
```

## Repères, limite et réactions

Les ancrages et axes sont locaux au repère de forme de chaque corps, comme
`Transform3D.point` et `Transform3D.vector` ; ils ne sont pas relatifs au
centre de masse. Pour une attache définie dans le monde, employer
`body.transform().inverse_point(point)` et `inverse_vector(axis)` sur chaque
corps. Les axes finis non nuls sont normalisés. Les valeurs par défaut sont
l’origine, Z et un demi-angle de π/4. `half_angle` appartient à [0, π] en
radians : 0 aligne les axes tout en laissant le twist libre, π ne borne pas
l’orientation. `angle()` retourne l’inclinaison non signée dans [0, π].

`anchor_error()` est le vecteur du premier ancrage vers le second, en mètres.
`reaction_force()` est la force en N exercée sur le second corps dans le monde.
`reaction_torque()` est le couple libre de limite en N·m sur ce même corps ;
le moment de la force d’ancrage n’est pas ajouté à ce couple. Les réactions
sont celles du dernier pas positif ; un pas nul les conserve. La famille cône
ne propose pas de moteur, de friction ou de ressort.

## Mutation et durée de vie

`set_anchors`, `set_axes`, `set_half_angle` et `set_enabled` invalident les
réactions et réveillent les corps liés. Désactiver la contrainte ou un corps
suspend sa résolution ; la destruction d’un corps ou du monde invalide le
handle. `World3D.destroy_cone_constraint` permet une destruction explicite.
La création demande deux corps distincts du même monde, dont au moins un
dynamique. Lire `is_valid()` avant de réutiliser un handle potentiellement
périmé ; les autres opérations sur un handle périmé échouent explicitement.

## Qualification

Le consommateur et le témoin Jolt épinglé couvrent twist libre, limites dans
les deux sens, charge, mutation du demi-angle, masses inégales, ancrage
excentré au repos et repère global tourné. Les tests supplémentaires couvrent
axes opposés, sommeil, contacts et destruction. La correction de position
est itérative ; les chaînes spatiales générales et l’égalité exacte des
réactions au pas d’impact ne sont pas garanties par ces témoins.
