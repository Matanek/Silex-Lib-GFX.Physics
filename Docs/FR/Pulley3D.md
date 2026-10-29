# Poulie 3D

`World3D.create_pulley_constraint` relie deux corps à deux points fixes du
monde. Sa longueur pondérée est L₁ + ratio × L₂. Par défaut, le câble peut
se détendre mais ne dépasse pas la longueur mesurée à la création. Un rapport
positif permet le palan : la seconde branche porte ratio fois la tension de
la première.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D()
    var first=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..transform=Physics.Transform3D(Math.Vec3(-1.0,0.0,0.0))
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var second=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..transform=Physics.Transform3D(Math.Vec3(1.0,0.0,0.0))
        ..mass_properties=Physics.MassProperties3D(4.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var joint=world.create_pulley_constraint(first,second,
        Physics.PulleyConstraint3DSettings(Math.Vec3(-1.0,2.0,0.0),Math.Vec3(1.0,2.0,0.0)) ..ratio=2.0)
    var i=0;while i<120 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.length()-6.0)<0.001 && Math.abs(joint.speed())<0.001)
    assert(Math.abs(joint.first_reaction_force().y-19.62)<0.001)
    assert(Math.abs(joint.reaction_force().y-39.24)<0.001)
    joint.set_limits(0.0,8.0);world.step(1.0/60.0)
    assert(joint.reaction_force().length()==0.0)
    joint.set_ratio(1.0);assert(joint.maximum_length()==8.0)
    world.destroy_pulley_constraint(joint);assert(!joint.is_valid())
    print("pulley recipe: ok")
}
```

## Ancrages et limites

`PulleyConstraint3DSettings(first_world_anchor, second_world_anchor)` demande
les deux points fixes. `first_local_anchor` et `second_local_anchor` sont
locaux aux repères de forme des corps, à l’origine par défaut. Les points
fixes ne suivent aucun corps. `ratio` est positif, vaut 1 par défaut ; son
carré doit être fini et non nul dans la représentation numérique.

`minimum_length` vaut 0 ; `maximum_length=null` capture la longueur pondérée
initiale. Les limites sont finies, ordonnées et non négatives. Deux limites
égales imposent une longueur rigide. Une limite minimale positive peut exercer
une poussée lorsque les branches deviennent trop courtes ; pour un câble qui
ne fait que tirer, conserver la limite minimale à 0. La géométrie de câble
doit rester représentable et finie.

`first_length()` et `second_length()` mesurent les branches en mètres ;
`length()` retourne leur somme pondérée et `speed()` sa variation en m/s,
avec les vitesses aux ancrages. Une branche de longueur nulle conserve la
dernière direction connue ; initialement et après une mutation, cette direction est −Y. C’est une
convention de singularité, pas une direction déduite d’un segment nul.
La famille n’ajoute pas de moteur, friction ou ressort.

## Réactions, mutation et durée de vie

`first_reaction_force()` et `reaction_force()` donnent les forces sur les
premier et second corps, dans le monde en N. `first_reaction_torque()` et
`reaction_torque()` donnent leurs moments aux ancrages en N·m ; ils incluent
le levier de la force et ne représentent pas un couple libre supplémentaire.
Ils enregistrent les impulsions réellement appliquées dans le dernier pas
positif ; un pas nul les conserve. Le jacobien de vitesse est préparé avant
l’intégration des poses, avec les leviers et réponses d’inertie de ce pas.
La correction de longueur n’ajoute pas d’énergie cinétique.

`set_local_anchors`, `set_world_anchors` et `set_ratio` conservent les limites
numériques déjà configurées. `set_limits` remplace les deux limites ; pour
recapturer un câble détendu, employer `set_limits(0.0, joint.length())`.
Toutes les mutations et `set_enabled` effacent les réactions et réveillent
les corps. La suspension d’un corps ou de la contrainte interrompt sa résolution.
Les getters d’ancrages, limites, ratio et état, `first_body`, `second_body` et
`is_valid` permettent l’observation ; `World3D.pulley_constraint_count` compte
les contraintes vivantes.

Créer avec deux corps distincts du même monde, dont un dynamique. Un corps
fixe peut retenir l’autre charge. Détruire un corps ou le monde invalide les
handles ; recycler un slot ne réactive pas un ancien handle. Les opérations
périmées échouent explicitement sauf `is_valid()` ;
`World3D.destroy_pulley_constraint` détruit explicitement une poulie.

## Qualification

Consommateurs et Jolt Debug/Release couvrent tension, mou, palan, masses
inégales, charge équilibrée ou machine d’Atwood, mutation de longueur,
ancrages excentrés et repère tourné. Projections de vitesse, efforts et
récurrences de déplacement sont vérifiés indépendamment. Les tests couvrent
limite inférieure, énergie, singularité, sommeil, durée de vie et contact réel
au sol. L’énergie analytique d’Atwood propage la tolérance de vitesse ; la
comparaison d’énergie avec Jolt garde sa borne de 0,05 J. Les chaînes spatiales
générales et la phase exacte des impacts restent hors de ces témoins.

Les [assemblages mixtes](TerrainConstraintQualification3D.md) ajoutent deux
guides SixDOF et le contact au sol, avec budgets de position explicités.
