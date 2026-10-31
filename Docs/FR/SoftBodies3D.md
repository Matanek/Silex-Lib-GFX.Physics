# Simuler un tissu ou un volume souple

`World3D` simule des particules reliées par des contraintes, avec les mêmes
corps rigides que le reste de votre scène. Le solveur CPU est écrit en Silex.
La définition réutilisable décrit la forme au repos ; chaque `SoftBody3D`
possède ses positions et vitesses indépendantes.

## Créer et présenter une forme

Les fabriques `SoftBody3DDefinition.cloth` et `cube` fournissent respectivement
une grille triangulée avec étirement, cisaillement et flexion, et un cube
composé de six tétraèdres. `vertex_mass` est la masse de chaque sommet mobile,
en kilogrammes. Dans une définition manuelle, `inverse_masses` contient les
inverses des masses ; zéro fixe un sommet. Sans cette liste, chaque sommet
possède une masse de 1 kg.

Le constructeur manuel prend les positions, les indices des triangles par
groupes de trois et les contraintes. `SoftEdge3D` conserve une distance ;
`SoftBend3D` conserve l’angle dièdre de deux triangles dont les deux premiers
indices forment l’arête commune ; `SoftVolume3D` conserve le volume orienté
d’un tétraèdre ; `SoftTether3D` limite la distance d’un sommet mobile à un
sommet fixe. Une compliance nulle donne une contrainte dure ; l’augmenter
assouplit la contrainte. Ces coefficients ne sont pas interchangeables entre
familles de contraintes.

Le [consommateur exécutable](../../Tests/Consumer/Tests/SoftBodies3D.sx)
montre la création sans fenêtre et les vérifications physiques. L’exemple
`Silex-Examples/Sources/Physics3D/SoftBodiesScene.sx` présente les formes avec
une caméra orbitale : Espace applique une impulsion, A active les attaches
mobiles, P suspend le temps et R recrée les instances.

`SoftBodyMesh3D(body, meshes)` crée un asset Scene3D. Utilisez `mesh()` dans
le composant Mesh3D puis appelez `update(meshes)` après les pas physiques. Cet appel
ne reconstruit le maillage que si les positions changent après le pas physique et retourne
alors `true`. Positions et normales sont recalculées ; les coordonnées sont
mondiales, donc l’objet graphique garde une transformation identité. Pour un
tissu visible des deux côtés, utilisez un matériau `double_sided`.
Le magasin est emprunté pendant chaque appel ; utilisez la même instance de `Meshes`
que lors de la création. `remove(meshes)` libère l’asset ; le présentateur ne le retire pas implicitement.

## Attacher, guider et agir

`set_fixed_position(vertex, position)` déplace un sommet de masse inverse
nulle ; le déplacement est interpolé entre les sous-pas. `attach(vertex,
body, local_point)` suit le repère d’un rigide du même monde. Cette attache
cinématique est pilotée dans un sens. Si le rigide disparaît, le sommet reste
à son dernier emplacement ; `detach(vertex)` le fige également sur place.

`set_pose` reçoit des `SoftPose3D` : cibles mondiales déjà calculées à partir
de la pose du squelette, avec une distance maximale de déviation et une
éventuelle sphère de butée arrière. Les cibles concernent des sommets mobiles distincts. Une distance nulle guide exactement le
sommet. Une liste vide retire le guidage. Les sommets non cités restent
simulés ; le mélange des os et des poids appartient au système d’animation.
Une collision peut déplacer un sommet guidé après la résolution de sa pose.

`apply_impulse(vertex, impulse)` agit sur un sommet mobile. Les réglages
contrôlent rayon de collision des sommets, amortissement, gravité, friction,
restitution, filtre et pression. La pression correspond au coefficient nRT,
avec une force proportionnelle à l’aire et inversement proportionnelle au
volume courant ; elle exige une surface fermée orientée vers l’extérieur.
`set_pressure` permet de la modifier pendant la simulation.

Les positions et vitesses se lisent par sommet ; `positions()` et les listes
de la définition sont des snapshots indépendants. `set_enabled(false)`
suspend une instance en conservant son état. `World3D.step(0)` ne modifie rien.
`destroy_soft_body` invalide le handle ; détruire le monde invalide toutes
ses instances, même si des handles ou présentateurs subsistent.

## Résolution et limites

`World3DSettings.soft_body_substeps` vaut 8 et accepte 1 à 128 sous-pas.
Davantage de sous-pas améliore la résolution au prix de calculs supplémentaires.
Les contraintes internes suivent un ordre stable par instance. Avec
`enable_parallelism`, les instances indépendantes se répartissent entre les
workers ; les contacts et impulsions rigides sont ensuite traités dans un
ordre canonique. Un même tissu conserve une résolution interne séquentielle.
Quelques instances dont les maillages demandent beaucoup de travail peuvent
déjà occuper plusieurs workers ; il n'est pas nécessaire de multiplier les
petites instances pour déclencher cette répartition.
Le pas reste synchrone et refuse les mutations du monde pendant son exécution.

Chaque sommet possède une sphère de collision. Il réagit aux formes rigides
actives autorisées par les filtres ; les capteurs ne produisent pas de réaction.
Les rigides dynamiques reçoivent les impulsions opposées, avec leur inertie.
Un balayage protège les déplacements rapides des sommets à travers les
obstacles fixes. Les mouvements rigides sont résolus avant le lot souple du
pas ; il ne s’agit pas d’une résolution simultanée de toutes les contraintes
rigides et souples.

Les obstacles fixes réutilisent leur préparation géométrique tant que leur
forme et leur pose ne changent pas. Les filtres, l’activation et les matériaux
restent ceux des corps courants. Le nombre de sous-pas et l’ordre des contacts
ne changent pas.

Les surfaces triangulées ont une couche arrière de récupération de 0,1 m, avec
des arêtes actives du côté avant, suivant la politique CPU de Jolt. Les requêtes
de monde existantes et les listes de contacts rigides concernent les rigides ;
le maillage Scene3D permet la sélection visuelle d’un tissu.

La surface entre sommets n’est pas un volume de collision continu. Réduire
l’espacement des sommets aide à couvrir un petit obstacle. Comme dans la
référence Jolt retenue, aucune auto-collision ou collision souple/souple n’est
fournie. Les joints articulaires rigides, les tiges orientées Cosserat, la
déchirure et la fracture ne font pas partie de cette API.

Une topologie invalide ou dégénérée, une masse/compliance invalide, une
pression sur une surface ouverte et une référence périmée provoquent un
panic, comme les autres contrats de création de ce package.
