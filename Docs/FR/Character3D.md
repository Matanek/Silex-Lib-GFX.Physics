# Déplacer un personnage 3D

`CharacterMover3D` déplace une capsule verticale dans un `World3D` :
il glisse contre les murs, bloque les plafonds, limite les pentes et franchit
les marches autorisées. Le programme conserve la position du centre et la
vitesse ; il décide de la gravité, du saut, des commandes et de la caméra.

## Appliquer un déplacement

Dans une boucle à pas fixe, ce fragment suppose un monde `world`, une position
`position`, une vitesse `velocity`, un état `grounded` et un intervalle `delta` :

```sx
var mover = Physics.CharacterMover3D(Physics.CharacterMover3DSettings()
    ..radius = 0.3 ..half_height = 0.55 ..step_height = 1.2)
let result = mover.calculate_move(world, position, velocity.multiply(delta), grounded)
position = result.position
grounded = result.grounded
velocity = result.clip_velocity(velocity)
```

Créer `mover` une fois, puis réutiliser l'instance. `half_height` est la moitié
de la partie cylindrique : ici la hauteur totale vaut 1,7 m. `position` est le
centre de la capsule, pas la position des pieds ou des yeux. Le résultat expose
également `ground_normal` et `stepped`. `clip_velocity` retire la vitesse dirigée
vers les surfaces rencontrées, sans ajouter la vitesse d'une marche artificielle.

Le [consommateur exécutable](../../Tests/Consumer/Tests/CharacterMover3D.sx)
couvre le déplacement et les collisions. L'exemple `World3D` du dépôt
Silex-Examples ajoute saut variable, contrôle aérien et caméra interpolée.

## Régler les appuis

- `max_slope_angle` est en radians, strictement entre 0 et π/2 ; défaut 45°.
- `step_height` vaut 0,4 m par défaut ; zéro désactive le franchissement.
- `step_forward` vaut 0,18 m : progression minimale tentée au-dessus d'une marche.
- `floor_snap` vaut 0,5 m : distance maximale de suivi descendant d'un appui.
- `skin` vaut 0,002 m et doit rester strictement entre zéro et le rayon.
- `filter` utilise `QueryFilter3D` et exclut les capteurs par défaut.

Le franchissement requiert un appui précédent et aucun déplacement ascendant.
La capsule doit pouvoir monter sans toucher un plafond et trouver un appui
franchissable au retour vers le bas. Le suivi du sol est désactivé pendant la
montée d'un saut. Une pente interdite ne transforme pas la poussée horizontale
en ascension. Un chevauchement initial est corrigé par passes bornées ; une
capsule profondément enfermée dans une géométrie ne garantit pas une sortie.

## Portée actuelle

Le contrôleur est virtuel et n'enregistre aucun corps rigide. Il lit les poses
courantes des boîtes, sphères, capsules et enfants de composés activés. Les corps
rencontrés sont traités comme des obstacles immobiles pour cet appel : il ne
les pousse pas et ne transporte pas encore le personnage avec un support mobile.
Mettre à jour le monde avant le déplacement si ses obstacles bougent.

La capsule garde sa forme et son axe vertical. Les personnages physiques, le
changement de forme, les interactions entre personnages et les supports mobiles
restent à implémenter. Aucun comportement de saut ou de caméra n'est imposé par
le package. Ne pas partager simultanément une instance entre plusieurs threads.
