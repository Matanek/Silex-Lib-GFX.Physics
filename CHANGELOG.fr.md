# Journal des versions de GFX.Physics

Ce journal commence à 0.7.0 et couvre les changements depuis le tag 0.6.0.
Les changements futurs sont consignés sous `## [Unreleased]` avant publication,
puis traduits dans `CHANGELOG.md`.

## [Unreleased]

- Accélération des mondes 3D chargés : recherche des paires par balayage de
  sphères englobantes et recherche ordonnée des contacts persistants. Une
  correction de position itérative empêche une colonne de 256 boîtes de
  s'enfoncer dans le sol ; le réveil suit aussi les contacts existants. Sur
  macOS ARM64, 1 024 sphères en bac passent de 27,82 à 11,67 ms par pas
  médian sans rendu ; 256 boîtes demandent 28,80 ms par pas.
- Ajout d'un ressort amorti à `DistanceConstraint3D`, réglable en fréquence
  et taux d'amortissement à la création ou pendant la simulation. La longueur
  exacte et les bornes souples d'une plage sont vérifiées ; une oscillation
  libre est comparée à Jolt épinglé en Debug et Release.
- Correction d'une vitesse tangentielle parasite après un choc frontal rapide
  contre une face à quatre points : le support normal multi-points est
  stabilisé avant la friction. Le projectile de la scène 3D ne dérive plus
  vers le haut après l'impact.
- Ajout d'un balayage linéaire optionnel des corps dynamiques pour arrêter une
  sphère rapide sur un mur mince et signaler les traversées complètes de
  capteurs dans un pas. L'arrêt est comparé à Jolt épinglé en Debug et Release ;
  l'absence d'événement Jolt sur le capteur rapide est documentée.
- Ajout de filtres de paires par catégories, masques et groupes, et de filtres
  de requêtes indépendants. Les corps capteurs émettent des événements de
  recouvrement sans réponse physique ; une traversée est comparée à Jolt
  épinglé en Debug et Release.
- Ajout des requêtes sur `World3D` : premier rayon, impacts multiples triés et
  recouvrements de formes, avec identité de corps/enfant, exclusion d'un corps
  et snapshots sûrs après destruction. Un cas de sélection est comparé à Jolt
  épinglé en Debug et Release.
- Ajout de `PointConstraint3D` : deux ancrages locaux coïncidents avec rotation
  libre, réaction, mutation et durée de vie sûre. L'articulation partage les
  contacts et le sommeil ; un appui et un pendule excentré sont comparés à Jolt
  épinglé en Debug et Release.
- Ajout de `DistanceConstraint3D` : ancrages locaux entre deux corps, longueur
  fixe ou plage rigide, force de réaction, mutation et invalidation sûre des
  handles. La contrainte partage les itérations des contacts et les îlots de
  sommeil ; le cas suspendu est comparé à Jolt épinglé en Debug et Release.
- Correction des appuis boîte–boîte inclinés : découpe de la face incidente,
  exclusion des coins au-dessus du support et réduction à quatre points. Le
  point représentatif d'un contact est le centroïde du manifold, ce qui évite
  un marqueur éloigné sur un grand sol.
- Ajout de `Plugins.Physics3D`, `Components.PhysicsBody3D` et des événements
  agrégés par frame pour relier le monde 3D à Application/ECS et aux poses
  Scene3D. Pas fixe, pause, rattrapage et coexistence 2D/3D sont vérifiés
  sans fenêtre ; une démonstration Scene3D est fournie dans Silex-Examples.
- Ajout des événements de début et de fin de contact 3D, lus après un pas via
  des snapshots `Contact3D` stables. La destruction programme la fin au pas
  suivant ; le recyclage et les ID d'enfants restent distincts.
- Ajout de `Compound3D` immuable pour assembler des sphères, boîtes et capsules
  sous un corps fixe. Les distances, recouvrements, rayons et contacts donnent
  l'identifiant de l'enfant retenu. Le composé dynamique reste à livrer.
- Ajout des valeurs `Sphere3D`, `Box3D`, `Shape3D` et `Transform3D` pour amorcer
  la géométrie 3D autonome. Les dimensions, poses et rotations invalides sont
  rejetées. `Geometry3D` fournit les distances signées, recouvrements et rayons
  pour sphères et boîtes orientées.
- Ajout d'un premier `World3D` autonome : corps fixes, cinématiques et
  dynamiques, masse et inertie des sphères/boîtes, forces, couples, impulsions,
  mouvement libre et handles invalidés à la destruction.
- Première réponse aux contacts sphère/boîte dans `World3D` : impulsion normale,
  correction de pénétration et observations de paire après le pas.
- Ajout de la friction et de la restitution par corps et dans les observations
  de contact. Le glissement est borné par la limite de Coulomb ; la restitution
  s'applique aux chocs suffisamment rapides.
- Les appuis boîte/boîte presque parallèles disposent de plusieurs points de
  contact, d'un solveur commun aux paires et d'impulsions reprises entre deux
  pas. `Contact3D.write_points` expose les points et leurs impulsions. Un petit
  empilement reste stable au pas fixe testé ; la collision continue linéaire
  est désormais optionnelle et ne couvre pas la rotation.
- Ajout du sommeil des corps dynamiques et de leurs îlots de contact, avec
  réveil par commande, collision ou changement de support. Le délai de repos
  et le réveil sont comparés à Jolt épinglé en Debug et Release.
- Ajout de `Capsule3D` verticale avec masse et inertie, requêtes autonomes de
  distance, recouvrement et rayon, et premiers contacts avec sphères, boîtes
  et capsules. Trois témoins capsule/boîte sont comparés à Jolt en Debug et Release.
- Ajout du composant ECS `TileMapCollider2D` : un corps fixe par carte, des rectangles solides fusionnés, une reconstruction sur édition et l’intégration au cycle d’activation des corps.

## [0.7.0] - 2026-09-24

### Pourquoi mettre à jour ?

Cette version étend l'intégration des mondes physiques dans une application,
renforce les contrats de durée de vie et corrige les contacts et contraintes.
Elle réduit aussi les copies et allocations temporaires dans les solveurs.

### Changements

- Les étapes physiques peuvent être suspendues sans rattrapage à la reprise
  ni anciens événements ; les corps ECS inactifs conservent leur état.
- Le déplacement des personnages dispose de réponses d'arrêt et de glissement,
  de hooks de pas fixe et de requêtes qui excluent le personnage lui-même.
- Les objets et instantanés peuvent porter des identités applicatives. Les
  compteurs de pas terminés et identités de corps sont exposés ; les options
  d'événements par corps et la rétention des abonnements sont renforcées.
- Les contacts des colliders composés restent indépendants. Les contacts
  spéculatifs, géométries dégénérées, joints moteur/souris et contraintes de
  distance sont corrigés ; les réactions de joints respectent leurs unités.
- Un pas de durée nulle est distingué d'une actualisation explicite des contacts.
  Les handles retenus sont invalidés lors de la finalisation du monde et les
  valeurs publiques invalides sont mieux contrôlées.
- Le solveur emprunte davantage les vues de corps et conserve les vitesses
  localement pendant les impulsions. Un monde sans joints évite le filtrage
  des collisions et les passes de joints inutiles. Les tests différentiels et
  les traces de déterminisme parallèle couvrent davantage de cas.

### Impact et migration

Vérifiez les usages des pas nuls, des événements, des handles après destruction
du monde et des observations de joints : cette version corrige leurs contrats,
pas seulement leurs performances. Consultez la documentation des fonctions
concernées sous `Docs/FR/`. Silex 0.47.0 est recommandé pour les corrections de
runtime et optimisations récentes ; le minimum déclaré reste 0.44.0.

Le [diagnostic d'allocation CCD](Benchmarks/Baselines/2026-09-24-native-heap.md)
mesure une amélioration du **compilateur**, à solveur identique. Ses chiffres
ne mesurent pas le gain global de GFX.Physics 0.7.0 face à 0.6.0.
