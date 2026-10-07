# Engrenage 3D

`World3D.create_gear_constraint` transmet la rotation de deux corps autour
de leurs axes locaux selon θ₁ + ratio × θ₂ = 0. Un rapport positif impose
des sens opposés ; un rapport négatif impose le même sens. Les angles sont
mesurés depuis les poses de création, en radians, avec suivi des tours.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var settings=Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0)
    var first=world.create_rigid_body(settings);var second=world.create_rigid_body(settings)
    var gear=world.create_gear_constraint(first,second,Physics.GearConstraint3DSettings() ..ratio=2.0)
    second.set_angular_velocity(Math.Vec3(0.0,0.0,1.0))
    world.step(1.0/60.0)
    assert(Math.abs(first.angular_velocity().z+0.4)<0.00001)
    assert(Math.abs(second.angular_velocity().z-0.2)<0.00001)
    assert(Math.abs(gear.first_reaction_torque().z+4.8)<0.0001)
    assert(Math.abs(gear.reaction_torque().z+9.6)<0.0001)
    assert(Math.abs(gear.phase_error())<0.00001 && Math.abs(gear.speed_error())<0.00001)
    gear.set_ratio(-1.0);world.step(1.0/60.0)
    assert(Math.abs(first.angular_velocity().z-second.angular_velocity().z)<0.00001)
    world.destroy_gear_constraint(gear);assert(!gear.is_valid())
    print("gear recipe: ok")
}
```

## Rapport, axes et réactions

`GearConstraint3DSettings` propose deux axes locaux au repère de forme,
Z par défaut, `ratio` signé non nul (1 par défaut) et `is_enabled`.
Les axes finis non nuls sont normalisés ; le rapport et son carré doivent
être finis et non nuls dans la représentation numérique.

La transmission ne retient ni les positions ni l'inclinaison des axes.
Pour des roues mécaniques, ajouter des charnières pour retenir les essieux.
Le suivi de phase suppose des rotations autour des axes déclarés ; les
témoins ne qualifient pas une chaîne dont les axes basculent librement.
Le rapport est celui des vitesses angulaires, pas un rayon ou un nombre
entier de dents imposé par l'API. Aucun contact de dents, moteur, friction
ou ressort n'est ajouté.

`phase_error()` est θ₁ + ratio × θ₂ en radians, `speed_error()` est
ω₁·axe₁ + ratio × ω₂·axe₂ en rad/s. Les poses externes sont interprétées
par le déplacement angulaire le plus court ; elles ne décrivent pas plusieurs
tours entre deux appels. Pendant un pas, le suivi emploie la vitesse intégrée
pour distinguer les tours, y compris au-delà de π rad par pas.
La correction de phase est progressive et n'ajoute pas d'énergie cinétique.

`first_reaction_torque()` retourne le couple sur le premier corps et
`reaction_torque()` celui sur le second, en N·m dans le monde. Les couples
sont axe₁ × λ/dt et axe₂ × ratio × λ/dt : la puissance totale est nulle
quand la relation de vitesse est satisfaite. Les réactions correspondent au
dernier pas positif ; un pas nul les conserve.

## Mutation et durée de vie

`set_ratio` et `set_axes` prennent les poses courantes comme nouvelle phase
zéro, effacent les réactions et réveillent les corps. `set_enabled` conserve
la phase : les tours effectués pendant la suspension restent observés, et
la remise en service récupère progressivement l'écart. Suspendre un corps
suspend aussi la résolution. Les getters exposent les corps, axes, rapport,
état et validité ; `World3D.gear_constraint_count` compte les attaches vivantes.

La création demande deux corps distincts du même monde, dont un dynamique.
Un corps fixe ou cinématique peut prescrire la rotation du corps dynamique.
La destruction d'un corps ou du monde invalide le handle ; les slots recyclés
ne réactivent pas un ancien handle. Toute lecture/mutation d'un handle périmé
échoue explicitement, sauf `is_valid()`.

## Qualification et frontière de référence

Les consommateurs vérifient rapports positifs/négatifs/fractionnaires,
inerties inégales, projection dissipative, puissance, phase et mutations,
sommeil, destruction et entraînement par charnières. Le témoin Jolt épinglé
compare les rapports unitaires, repères distincts et charges en Debug/Release.
Sa réponse non unitaire omet le facteur du second couple : un rapport −1
injecte de l'énergie. Cette divergence est conservée dans le harnais ; les
rapports concernés sont qualifiés par les équations mécaniques indépendantes,
sans revendiquer une parité avec cette réponse fautive. Les chaînes spatiales
générales et la phase exacte des impacts restent hors de ces témoins.
