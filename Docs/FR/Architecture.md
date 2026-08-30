# Architecture de GFX.Physics

`GFX.Physics` possède l’espace de noms `GFX.Physics` sous l’autorité de GFX.
La simulation reste indépendante de toute fenêtre, scène, renderer ou ECS.
L’API exprime les intentions physiques ; intégration numérique, stockage,
accélération spatiale, contacts et données du solver restent privés.

## Propriété et identités

`World2D` possède la simulation et son horloge. `RigidBody2D`, `Collider2D` et
les huit familles de joints sont des handles opaques générationnels. Les champs
chauds des corps et colliders vivent dans des tableaux denses ; supprimer une
valeur compacte ces tableaux, incrémente sa génération et invalide toute copie
ancienne sans exposer slot ni index.

Un corps possède zéro, un ou plusieurs colliders. Les mutations de topologie
marquent les données dérivées à reconstruire avant le prochain pas. Les
contacts publics sont des snapshots ordonnés par identité stable ; aucun nœud
de BVH, hash de paire ou indice dense ne traverse l’API.

## Géométrie, contacts et événements

La couche géométrique développe les formes en proxies convexes privés. Elle
utilise hull convexe, GJK, progression conservative et axes de faces. Les
chaînes sont unilatérales selon la convention de winding Box2D. Chaque requête
possède son scratch, ce qui permet des lectures parallèles indépendantes.

Les formes générales et corps composés utilisent le cycle persistant de
contacts. Les capteurs partagent géométrie et filtres sans entrer dans les
îlots ni le solver. Mouvements, débuts/fins de contact, impacts et transitions
de capteur sont des buffers déterministes postérieurs au pas et restent
optionnels.

Les bullets balayent les cibles dynamiques et la géométrie convexe. Les corps
ordinaires rapides conservent la garde continue plus étroite. Un monde sans
bullet quitte ce chemin immédiatement.

## Solver, parallélisme et sommeil

Le solver Soft Step unique exécute quatre sous-pas par défaut, warm start,
contraintes colorées, friction, restitution et relaxation. Les réglages du
monde permettent de choisir les sous-pas, la raideur, l’amortissement et les
limites de vitesse sans exposer l’ordonnancement interne. Les contacts
parallèles de
faces résolvent leurs deux impulsions normales ensemble. Contacts et joints
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

La réponse dynamique de toutes les nouvelles géométries, les forces externes,
les tissus, corps mous, fluides et la 3D restent hors du contrat courant. Le
profil optionnel n’expose que `motion_ms`, `broad_phase_ms`, `solve_ms`,
`sleep_ms` et leur total.
