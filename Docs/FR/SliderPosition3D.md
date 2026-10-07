# Servo de position de glissière 3D

`SliderMotor3D.position(position, maximum_force, stiffness, damping)` conduit
un chariot vers une course relative signée. La cible est en mètres sur X du
premier repère, la capacité symétrique en N, la raideur en N/m et
l'amortissement en N·s/m. Le [moteur vitesse](SliderMotor3D.md) reste disponible.

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
        Physics.SliderConstraint3DSettings() ..minimum_position = -1.0 ..maximum_position = 1.0
        ..motor = Physics.SliderMotor3D.position(0.75, 10.0, 8.0, 8.0))
    var step = 0
    while step < 720 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() - 0.75) < 0.0001)
    joint.set_motor(Physics.SliderMotor3D.position(-0.4, 10.0, 8.0, 8.0))
    step = 0
    while step < 720 { world.step(1.0 / 120.0); step++ }
    assert(Math.abs(joint.position() + 0.4) < 0.0001)
    assert(joint.motor()!.target_position == -0.4)
    joint.set_motor(null)
    assert(joint.motor_force() == 0.0)
}
```

Les quatre valeurs doivent être finies ; la raideur est strictement positive,
l'amortissement et la force maximale sont positifs ou nuls. Un amortissement
nul autorise l'oscillation ; une capacité nulle laisse la course libre.
`target_position`, `maximum_force`, `stiffness` et `damping` sont des valeurs
lisibles de la commande ; `speed` vaut zéro en mode position. En mode vitesse,
`target_position` vaut `null` et la raideur/amortissement valent zéro.

`joint.set_motor(...)` remplace la cible ou passe entre position, vitesse et
`null`, efface les réactions et réveille les corps. `joint.motor()` conserve
la cible demandée ; la cible effective est projetée entre les limites actives.
Une cible extérieure ne commande donc pas une force permanente contre la butée.
Les retenues, contacts réels et règles de références de la [glissière](Slider3D.md)
restent actives. La capacité borne la force cumulée sur tout le pas.

Le ressort et l'amortisseur sont physiques : une charge constante produit un
décalage d'équilibre égal à sa force divisée par la raideur. Si la capacité
ne suffit pas, le chariot peut continuer à reculer. `motor_force()` mesure
l'effort signé propre au servo ; `reaction_force()` inclut aussi les retenues
et butées. Le couple libre peut compenser un ancrage excentré. Une commande
position avec capacité positive maintient les corps éveillés, même à cible zéro.
Un pas nul conserve les mesures ; suspension et destruction suivent la glissière.

Les consommateurs vérifient récurrence à 60/120 Hz, oscillation non amortie,
saturation, charge, masse réduite, repères/COM 3D excentrés, limites, mutations,
sommeil, suspension et contacts. L'oracle Jolt qualifie huit cas à 60 Hz en
Debug/Release : amortissement critique et faible, saturation, modes successifs,
cibles limitées, charge, deux masses libres et ancrage excentré. La parité des
impacts, des transitoires sur rail tournant et des chaînes spatiales générales
reste à établir. Commande position/vitesse combinée et
butées souples restent à qualifier.

`SliderPositionScene.sx` compare un chariot doré fortement amorti à un chariot
bleu qui oscille ; les repères verts montrent la cible. T inverse la cible,
R réinitialise, Espace met en pause/reprend et Échap ferme.

Le [frein de glissière](SliderFriction3D.md) ralentit la course sans moteur avec une force maximale mutable.

Les [bornes de force signées](SliderForceBounds3D.md) règlent des efforts différents selon le sens, en vitesse et en position.
