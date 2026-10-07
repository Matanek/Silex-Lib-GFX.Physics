# Friction axiale de glissière 3D

`SliderConstraint3DSettings.maximum_friction_force` freine passivement la
course relative d'un chariot. La capacité symétrique est en N, finie et
positive ou nulle ; zéro, valeur par défaut, laisse la course libre.
La friction peut arrêter le mouvement et tenir une charge axiale inférieure
à sa capacité sans commander une position cible.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    carriage.set_linear_velocity(Math.Vec3(1.0, 0.0, 0.0))
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings() ..maximum_friction_force = 2.0)
    var step = 0
    while step < 240 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001)
    joint.set_maximum_friction_force(0.0)
    carriage.set_linear_velocity(Math.Vec3(-0.5, 0.0, 0.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() + 0.5) < 0.0001 && joint.friction_force() == 0.0)
    joint.set_maximum_friction_force(1.0)
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed()) < 0.0001 && joint.maximum_friction_force() == 1.0)
}
```

`maximum_friction_force()` lit la capacité et `set_maximum_friction_force(force)`
la remplace, efface les réactions et réveille les deux corps. Les réglages de
création sont copiés. `friction_force()` donne l'effort signé en N appliqué au
second corps pendant le dernier pas positif : il s'oppose à la vitesse relative
sur X du premier repère ou tient une charge au repos. Sa borne est commune à
toutes les passes du pas ; l'arrêt ne provoque pas une inversion de vitesse.

Un [moteur vitesse](SliderMotor3D.md) ou un [servo de position](SliderPosition3D.md)
installé prend priorité, même avec capacité nulle. `set_motor(null)` rend la
friction active à nouveau, avec la capacité conservée. Les efforts moteur et
friction sont mesurés séparément ; `reaction_force()` inclut aussi les retenues
et les butées. `reaction_torque()` peut compenser le moment d'un ancrage excentré.

Cette force de freinage axial se règle indépendamment de la friction matérielle
des contacts. Butées, contacts et règles de durée de vie de la
[glissière](Slider3D.md) restent actives. Un pas nul conserve les mesures ;
modifier les repères, limites ou activation les efface. Suspendre un corps
ou la contrainte remet les efforts à zéro au pas positif suivant. La friction
seule ne maintient pas artificiellement un assemblage immobile éveillé.

Les tests couvrent 60/120 Hz, signes, arrêt, charge, masse réduite,
COM/ancrage 3D excentré, mutations, priorité des moteurs, sommeil,
suspension, butées et contacts réels. L'oracle Jolt Debug/Release vérifie
huit trajectoires à 60 Hz : freinage signé, ancrage excentré, deux masses,
mutations, modes moteur, capacité nulle et tenue/libération d'une charge.
La parité des transitoires tournants, impacts et chaînes spatiales générales
reste à établir ; les autres extensions de glissière restent à qualifier.

`SliderFrictionScene.sx` montre un chariot doré sur un rail incliné. F active
ou retire le frein ; T relance alternativement vers le haut et vers le bas.
R redémarre, Espace met en pause/reprend et Échap ferme.

Les [bornes de force signées](SliderForceBounds3D.md) règlent des efforts différents selon le sens, en vitesse et en position.

[Butées souples de glissière](SliderSoftLimits3D.md) : compression sous charge, ressort amorti, bornes égales et mutation.
