# Journal des versions de GFX.Physics

Ce journal commence à 0.7.0 et couvre les changements depuis le tag 0.6.0.
Les changements futurs sont consignés sous `## [Unreleased]` avant publication,
puis traduits dans `CHANGELOG.md`.

## [Unreleased]

- `SphereCast3D` et `Geometry3D.sphere_cast` balayent un volume sphérique contre
  les formes qualifiées : premier impact face/arête/sommet, tangence, recouvrement
  initial et identités. `World3D.sphere_cast` ajoute filtres, exclusion et handle
  sûr avec snapshots. Requête bilatérale pour triangles, sans mutation du monde.

- Les composés acceptent des enfants convexes, seuls ou mêlés aux primitives :
  centre et tenseur complet, requêtes, IDs de feuilles, appuis maillage,
  capteurs, remplacement et CCD linéaire. Les bornes composent les poses des
  feuilles avant de les réunir, afin de conserver les décalages compensés
  et d’éviter des balayages exacts entre objets éloignés. Qualification
  Native Debug/Release et témoins Jolt de masse et géométrie sur macOS ARM64.

- Le maillage convexe écarte les faces éloignées avec des bornes conservatives,
  puis conserve le témoin exact le plus proche et son identité. Les directions
  d’arêtes strictement identiques ne sont stockées qu’une fois dans l’enveloppe
  immuable. Ces deux coûts ralentissaient fortement la nouvelle scène Debug ;
  les directions presque parallèles et le CCD restent actifs. Les projections
  SAT sur les faces de l’enveloppe sont partagées entre triangles pour chaque
  passe de contact, avec les mêmes axes et la même tolérance. Mesures de scène
  sur macOS ARM64 Native Debug/Release ; aucune borne par frame ou autre cible.

- Les convexes heurtent les maillages fixes : distance bilatérale et identité
  de face, quatre points d’appui sur les coutures planes, réactions distinctes
  dans une vallée et fusion à la crête. Les trous, capteurs, filtres et CCD
  linéaire respectent les faces présentes et leur côté admissible.
  `ConvexMeshScene.sx` montre le glissement, la vallée et un tétraèdre en rotation.

- Le CCD de translation écarte les paires dont les volumes parcourus ne se
  rencontrent pas avant de calculer leur distance exacte. Les bornes d’un
  convexe suivent ses vrais sommets, y compris une origine locale décalée.
  Cela supprime le ralentissement Debug de la scène à trois triangles.

- Une enveloppe convexe entre en contact avec un triangle fixe : distances
  bilatérales face/arête/sommet, profondeur de pénétration, manifold d’appui,
  rebond, capteurs, requêtes et CCD de translation unilatéral. Le centre du
  volume conserve le côté avant lorsque l’origine locale est décalée.
  `ConvexTriangleScene.sx` montre chute, rotation et passage de la face arrière.
  Convexe/maillage, coutures et enfants convexes restent à qualifier.

- Deux enveloppes convexes peuvent se rencontrer dans les deux ordres :
  distance extérieure euclidienne, profondeur d’inclusion, contacts de face
  jusqu’à quatre points et témoins d’arêtes. Le monde conserve les filtres,
  capteurs, événements et CCD de translation. `ConvexPairsScene.sx` montre
  un contact entre deux corps dynamiques et une plateforme cinématique portant
  un cube convexe. Les paires avec les terrains et les enfants convexes restent
  à qualifier ; les piles sans friction gardent les limites du solveur partagé.

- Les enveloppes convexes peuvent être cinématiques ou dynamiques face aux
  sphères, boîtes et capsules. La densité calcule leur masse, centre de masse
  et tenseur complet ; impulsions, mutations, capteurs et CCD linéaire suivent
  les mêmes commandes que les primitives. `MovingConvexScene.sx` montre chute,
  rotation et plateforme mobile. Les paires convexe/terrain,
  les enfants convexes et le CCD rotationnel restent à venir.
- La construction d’une enveloppe reconnaît une face par ses points de support,
  évitant une face doublée après rotation et translation d’un parallélépipède.

- `CharacterMover3D` se déplace et prend appui sur les convexes fixes : pentes,
  murs, marches et plafonds, glissement et récupération bornée. Les capteurs,
  filtres, retraits et changements d'état coupent l'appui. Le parcours montant
  et descendant concorde avec Jolt ; `CharacterConvexScene.sx` permet de
  l'essayer. Les personnages physiques restent à venir.

- Les capsules rencontrent les enveloppes convexes fixes : distances signées
  du segment axial entier, inclusion solide, appui de face à deux points,
  enfants capsules de composés et CCD linéaire. Une capsule rejoint la scène
  animée du coin. Les enfants convexes restent refusés.

- Les boîtes rencontrent les enveloppes convexes fixes : distances signées
  dans les deux ordres, appui jusqu’à quatre points sur les vraies faces,
  composés de boîtes et CCD linéaire. Une boîte animée rejoint la scène du coin.

- Le CCD 3D referme l’écart restant entre sa marge de recherche et la
  surface d’impact. Un rebond oblique sur un convexe est résolu dans le pas
  qui freine le déplacement, sans image d’accrochage avant l’impulsion.

- `ConvexHull3D(points)` ajoute une enveloppe solide immuable et
  `Shape3D.convex` : distances signées sphère/convexe, rayons et collisions
  contre un corps fixe, avec CCD linéaire, filtres et capteurs. Frontière
  triangulée accessible pour le rendu ; les enfants convexes de composés
  restent refusés.

- Le CCD linéaire respecte le côté avant des triangles et maillages fixes :
  sphères, boîtes et capsules rapides traversent les faces arrière et les
  ouvertures sans déplacement bridé ni événement fantôme. Une face arrière
  proche ne masque plus la face avant suivante ; les requêtes autonomes
  restent bilatérales. Poses inclinées et boîte enfant de composé qualifiées.

- Qualification des maillages plans ouverts : chute des boîtes, sphères et
  capsules dans un trou, boîte large sur ses bords et perte de contact au
  bord extérieur. Les appuis restent sur les faces présentes.

- Les boîtes conservent plusieurs contacts de surface sur un terrain lorsque
  les appuis diffèrent. Le repos dans une vallée à deux pans est qualifié
  contre Jolt Debug/Release, y compris ordres inversés et enfant de composé.
  Les réactions identiques des triangles coplanaires ou d’une crête sont
  fusionnées ; chaque appui conserve son ID de face et ses événements.
  Les capteurs exposent les mêmes surfaces sans correction.

- Les boîtes utilisent les distances et recouvrements bilatéraux contre
  triangle et maillage fixe. Le monde génère jusqu’à quatre appuis sur les
  faces coplanaires touchées : repos sur diagonale et glissement incliné sont
  qualifiés contre Jolt Debug/Release. `BoxTerrainScene` montre une pile et
  un parcours de grille. Les plis arbitraires et le CCD terrain restent ouverts.
  `RigidBody3D.same_body` emprunte son argument en lecture, ce qui permet de
  comparer directement une poignée issue d’un état emprunté.

- Les distances et recouvrements capsule–triangle et capsule–maillage
  couvrent tout le segment axial, les poses orientées et les deux ordres.
  Le monde répond du côté avant ; une capsule parallèle à une face plane
  peut reposer sur deux points. `CharacterMover3D` parcourt une grille
  inclinée dans les deux sens, avec un appui continu et une comparaison à
  Jolt à 5 mm près. La scène `CapsuleTerrainScene` permet d'essayer le saut
  et le mouvement manuel. Les boîtes sur terrain restent hors de cette tranche.

- `TriangleMesh3D.from_height_grid` construit une surface fixe depuis une
  grille régulière de hauteurs finies, avec identité déterministe des deux
  faces de chaque cellule. Une sphère franchit plusieurs coutures inclinées
  dans les deux sens sur un cas 4 × 4 comparé à Jolt Debug et Release.

- La couture entre deux triangles fixes avec une différence de hauteur de
  0,4 m est qualifiée dans les deux sens pour une sphère sans friction, avec
  identité de face et trajectoire comparées à Jolt Debug et Release.

- `TriangleMesh3D` réunit des triangles dans une forme fixe. Distance et rayon
  exposent l'index de face ; le monde choisit une face avant par sphère
  dynamique primitive ou enfant de composé. Le franchissement d'une couture plane de deux
  triangles conserve un appui unique sans double correction.

- `Triangle3D` ajoute une surface physique fixe orientable. Distance et
  recouvrement avec une sphère ainsi que rayon autonome couvrent face, arêtes
  et sommets ; le monde répond aux sphères dynamiques du côté avant uniquement.
  Les autres paires, composés triangulaires et mouvements du triangle restent
  hors de cette tranche.

- `RigidBody3D.set_shape` remplace la forme d'un corps vivant, notamment un
  composé modifié, sans changer son identité. La masse dynamique est recalculée
  depuis la densité ; les contacts précédents terminent au pas suivant et leurs
  impulsions ne sont pas réutilisées avec la nouvelle géométrie.

- Les composés 3D deviennent dynamiques avec masse, centre de masse et tenseur
  d'inertie complets issus des enfants orientés et décentrés. Les contacts
  conservent leurs identités de feuille. `MassProperties3D` accepte désormais
  un `Mat3` pour les inerties non diagonales tout en conservant les appels `Vec3`.

- `CharacterMover3D` suit désormais un support cinématique en translation ou
  rotation à partir de sa pose précédente et de l'identité du corps. Le
  résultat expose le corps d'appui par `support()` ; saut, retrait,
  désactivation et filtrage coupent le transport sans déplacement résiduel.

- Le glissement de capsule ne se bloque plus sur les faces inclinées et
  leurs arêtes lorsque le résidu de projection est inférieur au seuil de
  mouvement tangent : projection et détection de contact partagent le même seuil.
  La recherche de marche exige un appui à la hauteur du contact ; le sol situé
  derrière une arête ne déclenche plus une fausse montée.

- Le franchissement respecte désormais le déplacement horizontal demandé :
  la recherche d’appui au-delà du bord de capsule ne provoque plus de dash,
  même à basse vitesse. La correction de marche ne rajoute pas de vitesse
  verticale à partir de la normale sondée.

- `CharacterMover3D` ajoute le déplacement virtuel de capsule : glissement,
  plafonds, limite de pente, marches, suivi du sol et récupération bornée des
  pénétrations. Les commandes et le saut restent à l’application.

- Les composés 3D fixes et cinématiques conservent un manifold par paire
  d'enfants en contact, avec événements et warm start indépendants. Les
  composés cinématiques peuvent transporter et réveiller des corps dynamiques
  en translation ou en rotation.

- Le solveur 3D exploite la masse tangentielle scalaire et l'absence de couple
  normal des sphères centrées à inertie isotrope. Les sphères à centre de masse
  décalé ou inertie anisotrope conservent la réponse générale. Une grille
  spatiale privée recherche les voisins des mondes denses ; les grandes formes
  et coordonnées hors grille gardent une recherche conservative. Les paires
  restent ordonnées, sans changer cadence, itérations ni seuils de sommeil.

- Le warm start 3D reprojette la friction dans le plan tangent courant quand
  la normale tourne, pour éviter une composante artificielle de support.
  Les paires de sphères utilisent directement leurs centres et rayons pendant
  la détection et les corrections de position, sans reconstruire les placements
  et témoins inutiles à chaque itération. Les autres formes conservent leur
  chemin général ; cadence et nombre d'itérations restent identiques.

- Les contacts 3D mémorisent leurs identités de corps, réutilisent la recherche
  du contact précédent pour le warm start et lisent ses points sans tableau
  temporaire. Une fusion linéaire des contacts triés produit les événements
  de début et de fin, en conservant leur ordre et leurs identités.

- La recherche de paires 3D parcourt directement les intervalles triés,
  sans reconstruire un tableau actif pour chaque corps. Les paires, leur
  ordre et les tolérances de contact sont conservés.

- Les tenseurs d’inertie isotropes (cubes, sphères ou masses personnalisées)
  appliquent directement leur facteur scalaire, sans rotations inutiles.
  Les auxiliaires de résolution empruntent les corps pendant les itérations
  pour éviter la gestion répétée de références propriétaires. Les arrondis
  de l’inertie changent légèrement et peuvent modifier une trajectoire chaotique.

- Réduction du coût des contacts et du sommeil 3D : construction des îlots par
  union des contacts et contraintes, séparation SAT seule pendant la correction
  des boîtes et suppression des calculs d’impulsion sans effet sur les corps
  fixes ou cinématiques. Le solver conserve ses itérations et sa cadence.

- Réduction du coût des colonnes de boîtes 3D : bornes englobantes tenant
  compte de la rotation, rejet des boîtes séparées avant le calcul des
  témoins de distance, réutilisation des axes de collision et des données
  constantes du solver. Le nombre d'itérations, la friction et le pas de
  simulation restent identiques ; les requêtes publiques de distance gardent
  leurs témoins exacts. Sur macOS ARM64 Release, sept répétitions avant/après
  mesurent 29,36 → 12,71 ms/pas pour 256 boîtes ; le scénario avec basculement
  passe de 24,31 à 11,95 ms/pas, sans rendu.

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
