# Architecture de GFX.Physics

`GFX.Physics` possède l’espace de noms `GFX.Physics` sous l’autorité de GFX.
La simulation reste indépendante de toute fenêtre, scène, renderer ou ECS.
Le module optionnel `Application2D` dépend de `GFX.Application`, `GFX.ECS` et
`GFX.Scene2D`, mais cette couche orchestre le même `World2D` public sans entrer
dans son cœur headless.
L’API exprime les intentions physiques ; intégration numérique, stockage,
accélération spatiale, contacts et données du solver restent privés.

## Propriété et identités

`World2D` possède la simulation et son horloge. `RigidBody2D`, `Collider2D` et
les huit familles de joints sont des handles opaques générationnels. Les champs
chauds des corps et colliders vivent dans des tableaux denses ; supprimer une
valeur compacte ces tableaux, incrémente sa génération et invalide toute copie
ancienne sans exposer slot ni index.

Une vue somme `Joint2D` reconstruit les handles typés depuis leurs générations
vivantes pour l’énumération par monde ou corps. Les mutations runtime valident
les valeurs, effacent les impulsions devenues incompatibles et réveillent les
deux extrémités avant le prochain pas ; aucun état du solver n’est exposé.

Un corps possède zéro, un ou plusieurs colliders. Les mutations de topologie
marquent les données dérivées à reconstruire avant le prochain pas. Les
contacts publics sont des snapshots ordonnés par identité stable des
colliders ; manifold et impulsions terminés traversent l’API, mais aucun nœud
de BVH, hash de paire, indice dense ou cache mutable du solver.

## Géométrie, contacts et événements

La couche géométrique développe les formes en proxies convexes privés. Elle
utilise hull convexe, GJK, progression conservative et axes de faces. Les
chaînes sont unilatérales selon la convention de winding Box2D. Chaque requête
possède son scratch, ce qui permet des lectures parallèles indépendantes.

Les formes générales et corps composés utilisent le cycle persistant de
contacts. Les capteurs partagent géométrie et filtres sans entrer dans les
îlots ni le solver. Mouvements, débuts/fins de contact, impacts et transitions
de capteur sont des buffers déterministes postérieurs au pas et restent
optionnels. Ils conservent des snapshots autonomes de géométrie et de matériau
avec les handles générationnels de leurs colliders.

Le filtrage custom et le pré-solve sont strictement opt-in par collider. Le
monde les évalue dans l’ordre stable des paires, sur le thread propriétaire de
`step`, avant tout dispatch parallèle. Ils reçoivent des snapshots publics et
retournent une `ContactDecision2D` autonome ; le verrou du monde interdit toute
mutation réentrante. Les modes de combinaison appartiennent aux matériaux et
ne demandent aucun callback exécuté par un worker.

Les requêtes de monde parcourent les colliders vivants et écrivent des handles
ordonnés par identité de création dans des buffers consommateurs. Le filtre de
requête reste distinct du filtre de contact ; AABB, overlap de forme, ray cast
et shape cast ne révèlent ni proxy ni ordre interne. Les temporaires
appartiennent à chaque appel, ce qui autorise plusieurs lectures sur un monde
au repos, tandis que `step` verrouille cette frontière.

`CharacterMover2D` compose les overlaps et shape casts de monde autour d'une
capsule. La collecte de plans, leur résolution itérative bornée et l'application
du déplacement restent séparées. Le calcul ne mute ni le monde ni les corps ;
il renvoie une valeur que le contrôleur de gameplay applique à son propre état.

Les corps dynamiques rapides balaient toute la géométrie fixe et cinématique
convexe, translation et rotation comprises. Les bullets étendent ce même
chemin aux cibles dynamiques. Les corps lents et les paires dynamiques sans
bullet évitent ce coût.

## Solver, parallélisme et sommeil

Le solver Soft Step unique exécute quatre sous-pas par défaut, warm start,
contraintes colorées, friction, restitution et relaxation. Les réglages du
monde permettent de choisir les sous-pas, la raideur, l’amortissement et les
limites de vitesse sans exposer l’ordonnancement interne. Toutes les formes
partagent ce chemin ; les contacts parallèles de faces résolvent leurs deux
impulsions normales ensemble. La vitesse tangentielle des matériaux entraîne
les convoyeurs et leur résistance au roulement amortit la rotation relative.
Contacts et joints
partagent douze couleurs déterministes ; la dernière reste scalaire et
ordonnée.

Le nombre de workers ne sélectionne jamais un autre broad phase ni un autre
solver. Une grille réutilisable découvre les candidats dynamiques et l’arbre
AABB privé sert aux formes fixes. Les seuils de charge ne changent que la
répartition du même graphe.

Les corps éveillés sont rassemblés par identité stable. Les îlots de joints et
formes générales dorment atomiquement ; les contacts boîte/cercle peuvent
endormir localement les corps calmes d’une pile. Les caches d’impulsions sont
invalidés aux transitions veille/réveil.

## Origine et limites

Les algorithmes sont des adaptations Silex natives de Box2D 3.1.1 au commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`, utilisé seulement comme oracle MIT.
Le package ne lie ni ne distribue Box2D.

Les tissus, corps mous, fluides et la 3D restent hors du contrat courant. Le
profil optionnel n’expose que `motion_ms`, `broad_phase_ms`, `solve_ms`,
`sleep_ms` et leur total.
