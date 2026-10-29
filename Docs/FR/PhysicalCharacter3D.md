# Personnage physique 3D

`PhysicalCharacter3D` utilise une capsule dynamique du monde : la gravité, les
contacts et sa masse participent au solveur rigide. Les rotations physiques sont
bloquées ; une force excentrée peut le déplacer sans le faire basculer.
L’application choisit sa vitesse et ses règles de saut.

```sx
var character = world.create_physical_character(
    Physics.PhysicalCharacter3DSettings() ..mass = 70.0,
    Math.Vec3(0.0, 1.2, 0.0))
character.set_linear_velocity(Math.Vec3(2.0, character.linear_velocity().y, 0.0))
world.step(delta)
let grounded = character.is_grounded()
```

Le monde actualise les contacts et l’appui après chaque pas. `ground_state()`
distingue `grounded`, `steep`, `touching` et `airborne`. `ground_normal()`,
`ground_velocity()` et `support()` décrivent le support ; sa vitesse inclut la
rotation au point de contact. `contact_count()` et `contact(index)` donnent les
contacts du dernier pas. Une durée de pas nulle conserve cet état.

`max_slope_angle` vaut 45° et `support_distance` vaut 0,02 m par défaut : cette
dernière borne permet de conserver l’appui dans la marge des contacts. `mass`,
`friction`, `gravity_scale`, `collision_filter` et `allow_sleep` règlent le corps.
Les marches et le suivi géométrique appartiennent au [contrôleur virtuel](Character3D.md) ;
ce mode physique utilise les réactions et le recul du solveur rigide.

## Changer de capsule et déplacer le personnage

`try_resize(world, capsule, max_penetration:0.005)` conserve les pieds et la masse,
et refuse une forme dont le chevauchement dépasse la tolérance annoncée. Le refus
ne change ni pose ni forme. Le verrou angulaire reste actif après changement de
forme ou de masse. `set_position(position)` téléporte et oublie l’ancien appui.

`body()` fournit le corps pour les forces, impulsions, attaches et requêtes.
Conserver une capsule verticale et employer `try_resize` pour ses dimensions ;
remplacer arbitrairement sa forme contourne le contrat du personnage.

Le monde possède le corps. `world.destroy_physical_character(character)` le
retire avec ses contraintes, et `is_valid()` devient faux. Un retrait direct
via `destroy_rigid_body(character.body())` ou la fin du monde invalide aussi
le handle. Après retrait d’un support, `support()` retourne null et le personnage
n’est plus au sol. Les handles de contacts suivent les règles habituelles du monde.

[Consommateur exécutable](../../Tests/Consumer/Tests/PhysicalCharacter3D.sx) : chute,
repos, masse/recul, plans inclinés, plateforme, resize, filtres et durée de vie.
