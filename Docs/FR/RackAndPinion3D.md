# Crémaillère et pignon 3D

`World3D.create_rack_and_pinion_constraint(pinion, rack, settings)` transmet
une rotation à une course selon θ = ratio × course. Le rapport est signé,
en rad/m : un rayon primitif R correspond à |ratio| = 1/R. Son signe dépend
du sens de l’axe et de la rotation choisis.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var settings=Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0)
    var pinion=world.create_rigid_body(settings);var rack=world.create_rigid_body(settings)
    var joint=world.create_rack_and_pinion_constraint(pinion,rack,
        Physics.RackAndPinionConstraint3DSettings() ..ratio=2.0)
    rack.set_linear_velocity(Math.Vec3(1.0,0.0,0.0));world.step(1.0/60.0)
    assert(Math.abs(pinion.angular_velocity().z-10.0/7.0)<0.00001)
    assert(Math.abs(rack.linear_velocity().x-5.0/7.0)<0.00001)
    assert(Math.abs(joint.pinion_reaction_torque().z-120.0/7.0)<0.0001)
    assert(Math.abs(joint.reaction_force().x+240.0/7.0)<0.0001)
    assert(Math.abs(joint.pinion_angle()-2.0*joint.travel())<0.00001)
    joint.set_ratio(-1.0);assert(joint.travel()==0.0 && joint.pinion_angle()==0.0)
    world.step(1.0/60.0);assert(Math.abs(joint.speed_error())<0.00001)
    world.destroy_rack_and_pinion_constraint(joint);assert(!joint.is_valid())
    print("rack recipe: ok")
}
```

## Axes et usage mécanique

`RackAndPinionConstraint3DSettings` contient `pinion_local_axis` (Z),
`rack_local_axis` (X), `ratio` (1 rad/m) et `is_enabled`. Les axes sont locaux
au repère de forme et normalisés. Ils doivent être finis et non nuls ; le
rapport et son carré doivent être finis et non nuls dans le format numérique.

Retenir le pignon avec une charnière et la crémaillère avec une glissière :
le couplage fournit seulement la transmission. Il ne retient ni les centres
ni les autres rotations. La crémaillère doit garder son orientation, et le
pignon tourner autour de son axe. Les témoins ne qualifient pas des axes qui
basculent librement. Aucun contact de dents, moteur, friction ou ressort
supplémentaire n’est introduit ; piloter la charnière ou la glissière pour
entraîner le mécanisme.

`travel()` est le déplacement du centre de masse de la crémaillère depuis
sa position de référence, projeté sur son axe, en mètres. `pinion_angle()`
suit les tours depuis l’orientation de référence en radians.
`phase_error()` est θ − ratio × course, en radians ; `speed_error()` est
ωp·axep − ratio × vr·axer, en rad/s. Le suivi distingue les tours effectués
pendant un pas, même au-delà de π rad ; les poses externes utilisent leur
changement angulaire le plus court. La correction de phase est progressive
et n’ajoute pas d’énergie cinétique.

## Servo et rail borné

Le servo de charnière choisit le chemin angulaire court, même lorsqu’une
crémaillère possède une course limitée. De +2 vers −2 rad, ce chemin tourne
dans le sens positif ; une butée peut l’empêcher de rejoindre la cible.
Choisir les cibles en tenant compte du chemin et du rail. Aucun couplage ne
change silencieusement la convention du moteur ou n’ajoute une butée angulaire.

Le témoin de servo fort utilise un rapport de 2 rad/m, deux corps de 2 kg
et inertie isotrope 0,4 kg·m², des cibles ±1,5 rad, un plafond de 12 N·m,
une raideur de 15 et un amortissement de 8. Le rail ±0,6 m arrête le pignon à
±1,2 rad ; le couple statique attendu vaut ±4,5 N·m et la force transmise
±9 N. Les inversions, les réactions et le repos sont qualifiés à 60/120 Hz.
À 120 Hz, ce témoin conserve moins de 0,002 rad de phase à chaque pas.

Au premier franchissement, une avance libre peut précéder la correction de
pose. Le témoin à 60 Hz et celui historique ±2 rad à 120 Hz dépassent 0,002 rad
transitoirement dans Silex et Jolt. Ces échecs sont conservés ; les tolérances
ne sont pas élargies. Les comparaisons complètes qui dépassent leurs bornes
restent rejetées, tandis que le repos est comparé séparément après 2,5 s par
commande. Cela ne prouve ni une phase exacte des impacts ni des chaînes générales.

## Réactions et mutation

`pinion_reaction_torque()` est le couple sur le pignon en N·m,
`reaction_force()` la force sur la crémaillère en N, tous deux dans le monde.
Leurs impulsions sont axep × λ et −ratio × axer × λ. Leur puissance totale
est nulle lorsque la relation de vitesse est satisfaite. Les réactions sont
celles du dernier pas positif ; un pas nul les conserve.

`set_axes` et `set_ratio` prennent les poses actuelles comme nouvelle référence,
effacent les réactions et réveillent les corps. `set_enabled` conserve la
phase accumulée pendant la suspension ; réactiver récupère progressivement
l’écart. Suspendre un corps suspend aussi la résolution.
`pinion_body`, `rack_body`, les getters d’axes/rapport/état et `is_valid`
permettent l’observation ; `World3D.rack_and_pinion_constraint_count` compte
les transmissions vivantes.

Créer avec deux corps distincts du même monde, dont un dynamique. Un endpoint
fixe ou cinématique peut prescrire la vitesse de l’autre corps. Détruire un
corps ou le monde invalide le handle ; la réutilisation des slots ne réactive
pas les anciens handles. Les opérations périmées échouent explicitement,
sauf `is_valid()` ; `World3D.destroy_rack_and_pinion_constraint` détruit
explicitement la transmission.

## Qualification

Consommateurs et Jolt épinglé Debug/Release couvrent rapports signés et
fractionnaires, masses différentes, repère tourné, charge et réactions ; les
équations de projection et de déplacement sont vérifiées indépendamment.
Les tests ajoutent tours, phase, mutations, suspension, sommeil, durée de vie
et entraînement par charnière/glissière, avec butée ou contact d’obstacle.
Les chaînes spatiales générales et la phase exacte des impacts restent hors
de ces témoins. La divergence d’oracle engrenage n’affecte pas cette famille :
le Jolt épinglé applique ici le rapport à l’impulsion linéaire.
