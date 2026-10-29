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
if grounded { velocity.y = 0.0 }
let result = mover.calculate_move(world, position, velocity.multiply(delta), grounded)
position = result.position
grounded = result.grounded
velocity = result.clip_velocity(velocity)
```

Créer `mover` une fois, puis réutiliser l'instance. `half_height` est la moitié
de la partie cylindrique : ici la hauteur totale vaut 1,7 m. `position` est le
centre de la capsule, pas la position des pieds ou des yeux. Le résultat expose
également `ground_normal`, `stepped` et `support()`. `clip_velocity` retire la vitesse dirigée
vers les surfaces rencontrées, sans ajouter la vitesse d'une marche artificielle.

Le [consommateur exécutable](../../Tests/Consumer/Tests/CharacterMover3D.sx)
couvre le déplacement et les collisions. L'exemple `World3D` du dépôt
Silex-Examples ajoute saut variable, contrôle aérien et caméra interpolée.

Une grille inclinée 4 × 4 est parcourue dans les deux sens avec des positions
comparées à Jolt Debug et Release à 5 mm près. Le
[consommateur de terrain](../../Tests/Consumer/Tests/CapsuleTerrain3D.sx) couvre
les coutures et la perte d'appui. `Physics3D/CapsuleTerrainScene.sx` dans
Silex-Examples permet d'essayer le parcours et le saut. Pour une commande de
marche au sol, remettre la vitesse verticale à zéro avant le déplacement ;
une vitesse ascendante conservée après projection représente une intention
de montée et désactive le suivi descendant. La gravité et le saut restent
les règles de l'application.

Un convexe fixe peut servir de pente, mur, marche ou plafond. Le
[consommateur convexe](../../Tests/Consumer/Tests/CharacterConvex3D.sx) vérifie
le glissement, les angles, les limites de pente et de marche, la récupération
bornée d'un chevauchement et la perte d'appui. Le parcours sur une pente
`y=0,25z` concorde avec Jolt Debug et Release à 5 mm près dans les deux sens,
y compris après rotation horizontale. `Physics3D/CharacterConvexScene.sx` dans
Silex-Examples montre la marche automatique ; Tab passe au contrôle manuel,
WASD ou les flèches déplacent la capsule, Espace saute et R recommence.

## Régler les appuis

- `max_slope_angle` est en radians, strictement entre 0 et π/2 ; défaut 45°.
- `step_height` vaut 0,4 m par défaut ; zéro désactive le franchissement.
- `step_forward` vaut 0,18 m : portée de recherche d’un appui franchissable
  au-delà du bord arrondi de la capsule. Cette sonde ne rajoute aucun déplacement
  horizontal à la commande, même à basse vitesse.
- `floor_snap` vaut 0,5 m : distance maximale de suivi descendant d'un appui.
- `skin` vaut 0,002 m et doit rester strictement entre zéro et le rayon.
- `filter` utilise `QueryFilter3D` et exclut les capteurs par défaut.

Le franchissement requiert un appui précédent et aucun déplacement ascendant.
La capsule doit pouvoir monter sans toucher un plafond et trouver un appui
franchissable au retour vers le bas. Le suivi du sol est désactivé pendant la
montée d'un saut. Une pente interdite ne transforme pas la poussée horizontale
en ascension. Un chevauchement initial est corrigé par passes bornées ; une
capsule profondément enfermée dans une géométrie ne garantit pas une sortie.
Dans une boîte isolée, la récupération utilise désormais la profondeur du
volume entier et retrouve le même appui que son enveloppe convexe : la capsule
0,3/0,55 centrée à y=0,8 dans une boîte 4 × 2 × 4 sort à y=1,852, skin inclus.
Les huit passes restent bornées ; plusieurs obstacles incompatibles ou une sortie
trop éloignée peuvent encore laisser une pénétration résiduelle.

## Changer de capsule et téléporter

`capsule()` lit les dimensions courantes. `try_resize(world, position, capsule)`
conserve la position des pieds et retourne le nouveau centre, ou `null` si la
forme proposée pénètre un obstacle. Le refus conserve la forme et l’état de
support : sous un plafond bas, le personnage reste accroupi. La requête respecte
les capteurs, filtres et corps désactivés comme le déplacement ordinaire.

```sx
if let resized = mover.try_resize(world, position, Physics.Capsule3D(0.3, 0.15)) {
    position = resized
}
```

Le rayon doit rester supérieur à `skin`. La hauteur et la largeur peuvent changer,
y compris pendant le transport par une plateforme. Après une téléportation ou
avant de réutiliser l’instance pour un autre personnage, appeler `mover.reset()`
pour oublier l’ancien support. L’application reste propriétaire de `position`.
Le [consommateur de changement de capsule](../../Tests/Consumer/Tests/CharacterResize3D.sx)
couvre refus atomique, plafond, largeur, filtres et support mobile.

## Portée actuelle

Le contrôleur est virtuel et n'enregistre aucun corps rigide. Il lit les poses
courantes des boîtes, sphères, capsules et enfants de composés activés, ainsi
que les faces avant des triangles et maillages fixes et les enveloppes
convexes fixes. Un
support cinématique conserve le point du personnage dans son repère local entre
deux appels : sa translation et sa rotation transportent la capsule, même hors
du centre de rotation. Appeler `world.step(delta)` avant `calculate_move` et
réutiliser le même mover avec l'état `grounded` retourné. Le déplacement fourni
reste l'intention propre du personnage ; l'application ne lui ajoute pas la
vitesse de la plateforme. Un saut, un support retiré, désactivé ou exclu par le
filtre coupe le transport. `result.support()` retourne le corps qui a fourni
l'appui de cet appel, ou `null` ; comme tout handle de corps, vérifier
`is_valid()` avant de le réutiliser après une destruction possible.

Les autres corps rencontrés restent des obstacles à leur pose courante : le
contrôleur ne pousse pas les corps dynamiques et ne les suit pas comme supports
mobiles. La capsule conserve son axe vertical. Les personnages
physiques et les interactions entre personnages
restent à implémenter. Aucun comportement de saut ou de caméra n'est imposé
par le package. Ne pas partager simultanément une instance entre plusieurs
threads.
