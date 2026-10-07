# Bornes de force du moteur de glissière 3D

`SliderMotor3D(speed, minimum_force, maximum_force)` permet de pousser et
freiner avec des efforts différents selon le sens. La vitesse est en m/s ;
les deux bornes signées sont en N sur le second corps, le signe positif
augmentant la course le long de X du premier repère.

Le chariot atteint ici +0,6 m/s rapidement, puis revient lentement vers
−0,6 m/s, car le freinage négatif est limité à −0,5 N.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings() ..motor = Physics.SliderMotor3D(0.6, -0.5, 2.0))
    var step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.6) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D(-0.6, -0.5, 2.0))
    step = 0
    while step < 120 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.speed() - 0.35) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D.position(-0.4, -2.0, 8.0, 8.0, 8.0))
    step = 0
    while step < 960 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() + 0.4) < 0.001)
    assert(joint.motor()!.minimum_force == -2.0 && joint.motor()!.maximum_force == 8.0)
}
```

Après une seconde d'inversion, la vitesse reste +0,35 m/s : une borne de
force limite l'accélération, sans interdire une vitesse déjà présente.
Le servo final emploie les mêmes bornes signées avec une raideur de 8 N/m
et un amortissement de 8 N·s/m.

Les formes existantes `SliderMotor3D(speed, maximum_force)` et
`position(position, maximum_force, stiffness, damping)` restent symétriques :
`minimum_force == -maximum_force`. La nouvelle surcharge
`position(position, minimum_force, maximum_force, stiffness, damping)`
conserve le [ressort physique](SliderPosition3D.md). Les valeurs de commande
sont immuables et `joint.motor()` en retourne un instantané facultatif.

Les bornes doivent être finies et ordonnées. `maximum_force` désigne la borne
supérieure signée dans ces surcharges. `[0, F]` pousse sans tirer ;
`[-F, 0]` tire sans pousser ; `[0, 0]` laisse la course libre. Si zéro est
exclu, le moteur impose un effort même à sa vitesse ou position cible.
Des bornes égales imposent cette force constante. Le budget cumulé est
partagé sur tout le pas ; il n'est pas répété à chaque passe.

`set_motor(...)` remplace la commande, efface les réactions et réveille les
corps. Le moteur reste prioritaire sur la [friction axiale](SliderFriction3D.md),
y compris à `[0, 0]` ; `set_motor(null)` rétablit la friction configurée.
`motor_force()` mesure l'effort signé ; `reaction_force()` inclut aussi
retenues et butées. Une borne supérieure nulle ou négative reste active.
Un intervalle excluant zéro maintient les corps éveillés même à cible nulle ;
un intervalle nul peut laisser dormir. Un pas nul conserve les observations ;
suspension, destruction et mutations de repères/limites suivent la
[glissière](Slider3D.md).

Les tests vérifient les récurrences 60/120 Hz, intervalles unidirectionnels,
égaux ou de même signe, servo, masse réduite, ancrage/COM 3D, mutations,
sommeil, butées et contact réel. Huit trajectoires Jolt Debug/Release
vérifient en plus les deux traces par une mécanique indépendante avant
comparaison. La parité des impacts, transitoires tournants et chaînes
spatiales générales reste à établir ; commande combinée et butées souples
linéaires restent à qualifier.

`SliderForceBoundsScene.sx` compare le chariot doré à bornes [-0,5, 2] N au
bleu symétrique ±2 N. T inverse la vitesse cible, R réinitialise,
Espace pause/reprise et Échap ferme. Le doré inverse plus lentement son
mouvement lorsque l'effort négatif est requis.
