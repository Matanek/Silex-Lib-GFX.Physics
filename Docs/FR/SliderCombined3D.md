# Suivre une cible mobile sur une glissière

`SliderMotor3D.position_and_velocity` associe une position en mètres à une
vitesse relative signée en m/s. Actualiser les deux valeurs à chaque pas
permet de suivre une trajectoire avec moins de retard qu'un servo de position
seul. La course utilise l'axe X du premier repère, comme la glissière.

La recette suit une cible sinusoïdale. Elle se lance depuis la racine du
workspace avec `silex run Packages/GFX.Physics/Tests/Consumer/Smokes/SliderCombinedRecipe3D.sx`.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail,carriage)
    var step = 0
    let dt = 1.0/120.0
    while step<960 {
        let time = step as float*dt
        let position = 0.75*Math.sin(time*0.8)
        let speed = 0.6*Math.cos(time*0.8)
        joint.set_motor(Physics.SliderMotor3D.position_and_velocity(position,speed,20.0,8.0,4.0))
        world.step(dt)
        assert(Math.abs(joint.motor_force())<=20.0001 && joint.anchor_error().length()<0.0001)
        step++
    }
    joint.set_motor(Physics.SliderMotor3D.position_and_velocity(0.5,0.3,-2.0,3.0,8.0,8.0))
    assert(joint.motor()!.speed==0.3 && joint.motor()!.minimum_force== -2.0)
    print("Moving slider target followed with bounded combined position and velocity drive")
}

```

La capacité symétrique de 20 N borne l'effort sur tout le pas. La dernière
commande montre la forme à bornes signées : −2 N et +3 N. Raideur positive
finie en N/m, amortissement non négatif fini en N·s/m et commandes/bornes
finies sont obligatoires ; les bornes sont ordonnées. `motor()` conserve la
commande demandée et `motor_force()` mesure sa force signée.

La position cible est projetée sur les limites avant le calcul du ressort,
y compris avec [butées souples](SliderSoftLimits3D.md). La vitesse reste un
biais de commande : elle peut comprimer une butée souple ; une butée rigide
borne la course. Une vitesse nulle reproduit le [servo de position](SliderPosition3D.md).
Les moteurs prennent la priorité sur la friction passive, même à capacité zéro.
`set_motor` remplace la commande, efface les réactions et réveille les corps ;
`null` rend le contrôle à la friction. Suspension, pas nul et destruction
suivent les garanties de la [glissière](Slider3D.md).

Avec une position cible constante et une vitesse non nulle, le corps atteint
un équilibre décalé, et non un mouvement sans fin. Sans charge ni limite,
l'écart vaut `(damping + delta * stiffness) * speed / stiffness` pour un pas
fixe `delta`. Une charge ajoute son décalage force/raideur. Pour une cible
mobile, fournir sa position et sa dérivée avant chaque pas, comme ci-dessus.

Les consommateurs qualifient la récurrence à 60/120 Hz, la vitesse zéro, les
bornes signées, masses libres inégales, ancrage excentré, butées, mutations,
sommeil, suspension, friction et contact. Huit témoins Jolt à 60 Hz comparent
trajectoires et efforts en Native Debug/Release, avec récurrence indépendante.
Les impacts rigides, transitoires sur rail tournant et chaînes spatiales
générales restent à établir ; aucune parité de coût n'est revendiquée.

`SliderCombinedScene.sx` compare le doré combiné au bleu en position seule ;
les repères verts montrent la cible mobile. T inverse le sens et reprend,
R recommence et Espace met en pause/reprend, avec boutons et statut visibles.
