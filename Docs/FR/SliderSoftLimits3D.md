# Amortir les butées d'une glissière

`limit_spring` laisse une butée se comprimer sous la charge avant de ramener
le chariot. `SliderLimitSpring3D(stiffness, damping)` exprime une raideur en
N/m et un amortissement en N·s/m ; `null` conserve les butées rigides.

Ce moteur comprime la borne positive de 0,25 m puis la borne négative de
0,0625 m, car ses efforts autorisés diffèrent selon le sens.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail,carriage,Physics.SliderConstraint3DSettings()
        ..minimum_position = -0.3 ..maximum_position = 0.3
        ..limit_spring = Physics.SliderLimitSpring3D(stiffness:8.0,damping:8.0)
        ..motor = Physics.SliderMotor3D(speed:1.0,minimum_force:-0.5,maximum_force:2.0))
    var step = 0;while step<1200 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()-0.55)<0.001 && Math.abs(joint.limit_force()+2.0)<0.001)
    joint.set_motor(Physics.SliderMotor3D(-1.0,-0.5,2.0))
    step = 0;while step<1440 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()+0.3625)<0.001 && Math.abs(joint.limit_force()-0.5)<0.001)
    let spring = joint.limit_spring()!
    assert(spring.stiffness==8.0 && spring.damping==8.0)
    joint.set_limit_spring(null)
    step = 0;while step<120 { world.step(1.0/120.0);step++ }
    assert(Math.abs(joint.position()+0.3)<0.0001)
}
```

La force positive de 2 N et la raideur de 8 N/m donnent une déformation
de 0,25 m : le chariot se stabilise à 0,55 m malgré la borne nominale de
0,3 m. À l'inversion, l'effort négatif de 0,5 N produit une déformation de
0,0625 m. Retirer le ressort rétablit la butée rigide aux mêmes bornes.
Le [moteur signé](SliderForceBounds3D.md) et la butée gardent leurs efforts
distincts : `motor_force()` et `limit_force()`.

Une butée souple devient active lorsque la course atteint ou dépasse sa
borne au début du pas. Un franchissement depuis l'intérieur l'active au pas
suivant ; la pose n'est pas projetée sur la borne souple. La borne inférieure
pousse vers le positif et la supérieure vers le négatif, sur le second corps.
Une butée n'attire pas le chariot lorsqu'il repart vers l'intérieur.
Deux bornes égales créent un ressort bilatéral ; sans amortissement, il
oscille autour de cette course. Sans bornes, le ressort laisse la course libre.

La raideur doit être strictement positive et finie, l'amortissement non
négatif et fini. Le réglage est une valeur immuable ; `limit_spring()` renvoie
un instantané optionnel. `set_limit_spring(...)` remplace le réglage,
efface les réactions et réveille les corps. `set_limit_spring(null)` restaure
les butées rigides. Un pas nul conserve les observations. Suspension,
destruction, repères et mutations de bornes suivent les règles de la
[glissière](Slider3D.md). Les [moteurs](SliderMotor3D.md) ou la
[friction](SliderFriction3D.md) peuvent agir avec les butées souples ; le
ressort ne remplace pas leur budget. Les cibles du [servo](SliderPosition3D.md)
restent projetées dans l'intervalle nominal, même avec une butée souple.

Les tests vérifient les récurrences 60/120 Hz, oscillations et énergie,
dépassement dans les deux sens, masses différentes, ancrages/COM 3D,
charge, mutations, sommeil et contact réel. Huit trajectoires Jolt
Debug/Release sont aussi vérifiées contre la mécanique indépendante.
Les impacts rigides, transitoires de rails tournants et chaînes spatiales
générales restent hors de cette qualification. La commande combinée de
glissière reste à qualifier.

`SliderSoftLimitsScene.sx` compare le chariot doré amorti au bleu sans
amortissement : le premier se stabilise, le second oscille. T relance dans
le sens alterné, R réinitialise, Espace pause/reprise, Échap ferme.
