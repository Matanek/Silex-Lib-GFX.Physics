# Journal des versions de GFX.Physics

Ce journal commence à 0.7.0 et couvre les changements depuis le tag 0.6.0.
Les changements futurs sont consignés sous `## [Unreleased]` avant publication,
puis traduits dans `CHANGELOG.md`.

## [Unreleased]

- Corps souples et tissus CPU : définitions partagées, distances/flexion/volumes, attaches et pose partielle, pression, contacts avec les rigides et maillage Scene3D déformé. Les instances indépendantes utilisent les workers du monde ; pause et durées de vie restent explicites.

- `World3D.enable_parallelism` répartit l’intégration, la géométrie et les lignes indépendantes du solveur de vitesses sur les workers STD. Les états et observations conservent leur ordre ; `step` reste synchrone et le retour à un worker ferme le pool. Guide et qualifications dédiés.

- Qualification des terrains édités et des assemblages SixDOF/poulie/sol et chemin/charnière/obstacle : témoins analytiques et Jolt, budgets de position explicites, mutations et retrait des corps. Le guide bilingue récapitule les douze familles et les limites des recettes.

- Les grilles de terrain sélectionnent leurs cellules pour les rayons, balayages et contacts, avec identités conservées et témoins exhaustifs sur des reliefs irréguliers. Le rayon des maillages et les bornes des grilles sont réutilisés entre pas.

- `HeightField3D` ajoute des versions de terrain par hauteurs : éditions locales de niveaux et de trous, anciennes formes conservées et publication explicite par `set_shape`. Les grilles évaluent leurs triangles depuis des échantillons copiés. La distance des calottes exposées de capsules effilées aux triangles utilise son certificat analytique, pour conserver les contacts CCD aux bords de terrain.

- Qualification des modes personnages et de leurs interactions, avec matrice des différences, consommateur GFX à pas fixe et comparaison Jolt des poussées, du poids, des masses, du repos et du changement de capsule en Native Debug/Release. Les déplacements acceptent un monde emprunté, y compris la ressource GFX, sans transfert de propriété.

- `VirtualCharacter3D` enregistre une capsule cinématique pilotée avec le mover, exclue de ses propres requêtes. Les personnages virtuels et physiques se rencontrent via les mêmes corps et filtres réciproques. Pas de double déplacement, resize conservant les pieds, contacts conservés pendant la pause et durées de vie vérifiés.

- `PhysicalCharacter3D` ajoute une capsule dynamique propriétaire du monde, à rotations physiques bloquées et masse réelle. Contacts/appui après simulation, pente, plateforme, resize conservant les pieds et la masse, téléportation et durées de vie sont couverts par un consommateur.

- `CharacterMover3D.move` ajoute poussée bornée, masse virtuelle et suivi des supports dynamiques. Les résultats exposent des contacts possédés ; le budget de poussée est partagé par corps composé. La requête `calculate_move` reste sans impulsions. Poids, masse effective, symétries, pause et durée de vie sont vérifiés.

- Le personnage virtuel peut changer de capsule en conservant les pieds : `try_resize` retourne le nouveau centre ou refuse atomiquement une forme bloquée. `capsule()` lit les dimensions courantes et `reset()` oublie le support après téléportation. Plafond bas, largeur, filtres/capteurs et transport cinématique sont vérifiés.

- Les inclusions capsule/boîte utilisent la profondeur de sortie du segment entier et de son rayon, avec axes de faces et d’arêtes extrudées. Les sphères et capsules incluses suivent la normale signée de réponse dès la requête géométrique ; le monde ne la retourne plus une seconde fois. Une capsule profondément incluse retrouve son appui sans oscillation, comme sur une boîte convexe identique. Tests analytiques, requêtes inversées, rotations, trois échelles et deux ordres de création des corps.

- Les corrections de position réévaluent les candidats de collision lorsqu’une articulation crée une pénétration après la détection initiale. Les plans et boîtes réagissent tout en respectant capteurs, filtres et supports désactivés ; aucune impulsion d’impact rétroactive n’est publiée.

- Les butées SwingTwist corrigent la rotation avec la masse couplée de l’ancrage déporté, afin que la projection de point n’annule pas leur correction. Parent fixe ou mobile, deux repères, deux sens et 60/120 Hz vérifiés ; les translations libres SixDOF restent indépendantes.

- Les axes presque parallèles des solides de révolution passent par le calcul 3D : le raccourci méridien 2D est réservé aux axes exactement parallèles. Cela évite une non-convergence entre deux couvercles légèrement inclinés, avec témoins analytiques dans les deux ordres, plusieurs échelles et repères.

- La correction de pénétration 3D tient compte des inerties et des bras de levier au point de contact. La correction commune aux deux corps conserve les profondeurs de chaque point selon la face de référence du clipping, y compris les enfants composés et les pans de maillage distincts. Une colonne articulée motorisée ne se propulse plus au repos : tests sur plan/boîte, deux ordres de création, 60/120 Hz, énergie, translations libres et lifetime. Les valeurs par défaut des itérations restent inchangées.

- Les roues réagissent aussi par leurs flancs aux contacts transversaux ou opposés à la détente : elles ne traversent plus le sol de côté pendant un retournement. Réactions au châssis et aux obstacles mobiles, filtres et exclusions vérifiés ; appuis de suspension inchangés. `side_collision_width` active cette protection pour les balayages rayon, sphère et cylindre ; le défaut `null` conserve leur comportement. Collisions latérales discrètes, sans corps ni événements de contact supplémentaires.

- Les contacts cylindriques de roue ignorent les chevauchements dont la normale s’éloigne dans le sens de détente de la suspension. Une voiture retournée ne reçoit plus de faux appuis alternés sur son toit ; les appuis légitimes au plafond et les chevauchements comprimés restent pris en charge.

- Qualification des trois familles de véhicules sur les terrains retenus et en conduite composée à adhérence variable ; campagne mixte de commandes, sommeil/réveil et destruction/recréation. Les profils rayon/sphère couvrent la conduite jusqu’à l’arrêt ; la parité des trajectoires cylindriques et le repos moto à cylindre large restent explicitement non qualifiés. Documentation des profils et de la durée de vie des snapshots synchronisée.

- Les rayons ne perdent plus les intérieurs de grands triangles à cause de la reconstruction du point le plus proche. La réduction des simplexes minces calcule en `float64` les orientations, les poids et les projections avant l’arrondi de sortie, ce qui supprime les contacts de roue aberrants sur grande face ou maillage. Le classement des faces conserve leur distance en précision accrue pour éviter une non-convergence EPA due à l’arrondi. Les balayages axiaux conservent aussi la normale exacte d’une face lorsqu’elle fournit un appui commun aux deux formes, sans amplifier le résidu du point le plus proche. Cette révision de développement nécessite le compilateur qui fournit `round_float<T>`.

- Précharge, modes fréquence/amortissement relatif et coefficients normalisés à la masse, et point local optionnel des forces de roue. Réglages communs aux voitures, motos et chenilles ; coefficients SI et contact réel conservés par défaut. Équilibres, conservation sur support dynamique, paramètres invalides et neuf recettes Jolt Native Debug/Release contrôlés.

- L’assistance d’équilibre moto conserve les très petits angles d’inclinaison : le calcul signé utilise atan2 de la norme du produit vectoriel et du produit scalaire, sans zone morte due à acos en simple précision. Réponse analytique comparée avec assistance coupée à ±1e−5/±1e−4 rad, sans changer les gains.

- Les roues verrouillées conservent leur effort de friction statique lorsque les autres contacts changent le signe d’une très faible vitesse résiduelle. Les impulsions cumulées restent bornées par la même adhérence et le même couple de frein ; le test miroir sur support tournant couvre le freinage jusqu’au repos sans augmenter les itérations par défaut. L’adhérence combinée applique ensemble les deux composantes du candidat, même à l’intérieur de l’ellipse, pour conserver les limites et le bilan du rotor.

- Les faces planes des boîtes, convexes et cylindres conservent des points candidats proches du plan avec leur écart individuel : une face chargée reste portante sans bloquer les coins encore en rapprochement. Les contacts de plan persistants participent avant l’intégration même sans articulation ; régression sous charge excentrée, impulsions et ordres de création opposés. Le défaut de 12 itérations reste inchangé.

- Adhérence combinée optionnelle par pneu avec `Tire3DSettings(combined_friction:true)` : traction/freinage et virage partagent une ellipse d’efforts ; une roue bloquée peut dériver. Bilans des rotors et réactions conservés ; modèle indépendant par défaut inchangé.

- Ajout de `Motorcycle3D` : deux roues suspendues, assistance d’équilibre réglable et désactivable, direction limitée selon la vitesse et réutilisation du moteur/transmission à roue arrière. Qualification initiale de l’équilibre et de la direction sur plan/rayon, à couple moteur nul, contre Jolt à 60/120 Hz en Native Debug/Release ; durée de vie, réglages et paramètres invalides contrôlés.

- Ajout de `TrackedVehicle3D` : deux bandes de roues suspendues, moteur et boîte partagés, vitesses relatives, contre-rotation et freinage. États par roue/bande, durée de vie et paramètres invalides contrôlés ; comparaison Jolt en vol et sur plan à contacts rayon, Native Debug/Release.

- Limite optionnelle d’inclinaison totale sur `WheeledVehicle3D` : cône relatif à la gravité, lacet libre, mutation de l’angle et haut local configurable ; correction progressive en vol ou avec appuis, défaut pi inchangé et singularité du retournement exact documentée.

- Barres anti-roulis optionnelles entre paires de roues : transfert dans les ressorts, perte d’appui et réactions dynamiques qualifiés face à Jolt ; réglages copiés, paires disjointes et raideur nulle sans effet.

- Contacts cylindriques optionnels par roue avec `WheelContact3D.cylinder(largeur)` : largeur réelle, braquage et carrossage, filtres et réactions ; balayages de grandes faces inclinées et normales radiales corrigés. La géométrie cylindrique exacte ignore le filtre de pente des rayons/sphères. Qualification Jolt et limites des contacts linéiques documentées.

- Contacts sphériques optionnels par roue avec `WheelContact3D.sphere(rayon)` : portée autour des arêtes, sélection des pentes et chevauchements initiaux, réactions et réglages validés. Les sphères balayées conservent les points intérieurs des grandes faces sans les rejeter à cause d’une reconstruction barycentrique arrondie ; le contact par rayon reste le défaut.

- Moteur, embrayage, transmission automatique/manuelle et différentiels optionnels pour `WheeledVehicle3D`, avec accélérateur persistant, régime et couples de roue observables. Les contacts transmettent la propulsion ; point mort, freinage, sommeil et durée de vie restent intégrés au monde.

- Commandes persistantes de braquage, frein et frein à main sur `WheeledVehicle3D`, réglages par roue et observations d’angle/couple. Le frein agit sur le rotor et le contact transmet l’effort dans la limite de l’adhérence ; pas de freinage artificiel du châssis.

- Pneus passifs optionnels sur `Wheel3DSettings` : inertie, amortissement et rotation, courbes de friction longitudinale/latérale, efforts tangentiels et réactions sur les supports. Le monde possède leur pas et leur sommeil ; réglages et durée de vie validés.

- `WheeledVehicle3D` associe un châssis dynamique et des suspensions de roue à contacts par rayon, ressorts unilatéraux et butées de compression. Appuis, longueurs et forces lisibles ; réaction sur les supports dynamiques, sommeil et durée de vie intégrés au monde. Premier socle de suspension qualifié face à Jolt à 60/120 Hz en Debug/Release sur macOS ARM64.

- `Ragdoll3D.move_to_pose` et `move_to_local_pose` déplacent une pose cinématique sur une durée ; `resume_simulation` reprend les membres dynamiques avec leurs masses et vitesses courantes. Repères tournés, centres décalés, contact extérieur et relâchement qualifiés face à Jolt à 60/120 Hz en Debug/Release sur macOS ARM64.

- Ragdoll motorisé spatial : repères non parallèles, cibles swing/twist combinées, appuis triangulaires et impulsion oblique qualifiés face à Jolt à 60/120 Hz en Debug/Release sur macOS ARM64. Géométrie et réactions moyennes sur fenêtres établies, bilans autour du barycentre et composante Y globale ; solveur et budgets existants conservés.

- `World3DSettings.velocity_iterations` règle la convergence des contacts et articulations, de 1 à 128 tours par phase, avec défaut 12 conservé. Une chaîne entièrement mobile à deux moteurs contre le sol utilise 48 tours pour qualifier ancrages, limites, réactions moyennes et perte/reprise du contact face à Jolt à 60/120 Hz en Debug/Release. Aucun gain de performance ni parité générale aux impacts revendiqué.

- Chaîne ragdoll libre à deux articulations swing/twist bornées : impulsions obliques opposées, butées exercées et bilans globaux de mouvement/énergie qualifiés face à Jolt à 60/120 Hz en Debug/Release. Les contacts et trajectoires d’impact générales restent ouverts ; solveur et API inchangés.

- Un membre ragdoll déporté à racine fixe compose cibles swing/twist bornées, contact au sol, levée, retour et relâchement sous impulsion. Géométrie et équilibres moyennés sur fenêtres fixes sont qualifiés face à Jolt à 60/120 Hz en Debug/Release ; l’égalité instantanée des vitesses/efforts et les impacts généraux restent ouverts. Solveur et API inchangés.

- Deux butées de torsion asymétriques dans un ragdoll passif sont qualifiées sous impulsions angulaires opposées face à Jolt : transmission aux parents, moment cinétique, énergie et états stabilisés, à 60/120 Hz dans deux orientations mondiales en Debug/Release. Aucun contact ni changement de solveur.

- `Ragdoll3D.drive_to_pose` et `drive_to_local_pose` suivent les rotations cibles avec des couples bornés, sans téléportation ; `stop_motors` rend les articulations passives. Les poses stabilisées d’une chaîne décalée sous gravité sont comparées à Jolt à 60/120 Hz en Debug/Release.

- `World3DSettings.position_iterations` permet de régler la correction des contacts et articulations à la création du monde, de 1 à 128 passes, avec la valeur par défaut de 4 conservée. Le parcours ragdoll avec impacts, limites anatomiques et collisions internes non voisines emploie 32 passes.

- Ragdoll passif de trois sphères : impulsion excentrée, transmission, bilans de mouvement, ancrages et chute symétrique sur un sol qualifiés face à Jolt à 60/120 Hz en Debug/Release ; solveur inchangé.

- Hiérarchie ragdoll réutilisable : poses mondiales/locales, décalages de corps et centres de masse, instances indépendantes, filtrage parent/enfant et durée de vie sûre ; conventions de pose et paires autorisées comparées au ragdoll Jolt en Debug/Release.

- Adopte la déclaration `Result` unique : l’appel ordinaire rend la valeur
  ou arrête le programme sur erreur ; `try appel()` conserve le `Result`. Les
  anciens appels stockant un résultat et propagations deviennent explicites.
  Cette révision requiert la toolchain de développement avec cette sémantique
  de `try` ; sa publication doit coordonner les versions du compilateur et des
  packages.

- Les charnières portées par un corps tournant transportent leur couple mémorisé dans le repère courant et conservent des axes cohérents pendant le pas. Une épaule swing/twist et un coude motorisés sous gravité sont qualifiés à 60/120 Hz contre Jolt, avec budgets, réactions et bilans séparés par phase.

- Trois servos swing/twist simultanés sous gravité : ancrage déporté, repères tournés, inversion et recentrage, réactions et régimes établis qualifiés à 60/120 Hz contre Jolt ; temporalité des bras de levier explicitée, sans changement du solveur.

- Chaîne spatiale charnière/glissière verticale sous charge déportée : gravité, contact au plan, inversion, réactions vectorielles et budgets qualifiés à 60/120 Hz contre Jolt, sans changement de solveur.

- Une chaîne de charnières motorisées conserve son bras retenu par un moteur de vitesse nulle pendant une poussée prolongée contre un plan : l’appui persistant participe au solveur avant intégration. Efforts conservés sans double application, téléportations invalidant le cache, recette et bilans à 60/120 Hz qualifiés contre Jolt.

- Contact puis libération dans une chaîne à deux charnières perpendiculaires : bilans avec impulsions et points de contact, charges et inversion qualifiés à 60/120 Hz contre Jolt ; recette et limites documentées, solveur inchangé.
- Chaîne de deux charnières perpendiculaires sous charge : bilans de force, rotation propre et moment total, réactions et inversion qualifiés à 60/120 Hz contre Jolt ; recette spatiale sans contacts documentée, solveur inchangé.

- Rail dynamique retenu sous gravité, avec impact axial et libération d’une paroi : bilans, réactions de poids, budgets et contact réel qualifiés à 60/120 Hz ; impulsions Silex mesurées et Jolt inférées distinguées, recette plane documentée sans changement du solveur.

- Qualification d’un rail dynamique sur charnière portant un chariot motorisé : moment cinétique, réactions et budgets vérifiés avec deux masses à 60/120 Hz, en rotation libre ou entraînée ; recette plane et écarts transitoires explicités, solveur inchangé.

- Rails fixes et tournants à ±0,2 rad/s : bilan d’impulsion mondial, freinage moteur et mouvement libre analytique qualifiés à 60/120 Hz ; repères d’application et d’observation distingués, écarts transitoires Jolt conservés sans modification du solveur.

- Impacts des butées rigides de charnière : bilan d’impulsion, travail dissipatif et sortie de butée qualifiés à 60/120 Hz ; activation anticipée explicitée et écarts Jolt conservés, sans modification du solveur.

- Qualification du servo de crémaillère avec deux butées et inversion : chemin angulaire court explicite, réactions statiques et repos comparés à Jolt à 60/120 Hz ; écarts transitoires conservés sans changement du solveur.

- Une charnière rejette l’effort mémorisé d’une butée souple devenue inactive ou opposée après mutation du corps ; le déplacement dans la zone libre ne conserve aucun couple de l’ancienne butée.

- Les charnières 3D convergent avec une charge fixe hors du plan sous gravité ; préparation passive, réactions et budget moteur conservés avec changement de pas et mutations. Qualification mécanique complète et comparaison Jolt après convergence ; écarts initiaux conservés.

- Guidage sur chemin 3D : Hermite ouvert/bouclé, distances et moteurs en mètres, friction, extrémités, transport physique d’orientation, mutations et témoins explicites des écarts Jolt.

- Poulie 3D : longueur pondérée à limites, câble détendu ou rigide, rapport de palan, ancrages et réactions physiques, mutations sûres et témoins Jolt.

- Crémaillère/pignon 3D : rapport signé en rad/m, phase suivie, couple et force physiques, mutations sûres et témoins Jolt.

- Engrenage 3D : rapport signé, suivi des tours, couples physiques et mutations sûres ; divergence du Jolt épinglé sur les rapports non unitaires conservée explicitement.

- Attache six degrés 3D : translations libres/verrouillées/bornées, moteurs par axe, friction et butées linéaires souples ; les pyramides angulaires acceptent les plages hors zéro et les angles verrouillés non nuls.

- Articulation swing/twist 3D : repères locaux, cône elliptique/pyramide, torsion bornée, moteurs séparés et friction passive ; preuves sans rendu.

- Articulation cône 3D : inclinaison bornée, twist libre, ancrages locaux, réactions et mutations sûres ; consommateurs et oracle Jolt sans rendu.

- La glissière suit ensemble une position et une vitesse avec `SliderMotor3D.position_and_velocity`, capacité symétrique ou bornes signées et ressort physique ; poursuite, mutations, contacts et oracle Jolt qualifiés.

- Butées souples de glissière : raideur/amortissement physiques, lecture/mutation, effort signé et coexistence avec moteurs/contacts.

- Le moteur de glissière accepte des bornes de force signées en vitesse et position, avec formes symétriques compatibles, effort imposé, mutation/réveil, contact réel et oracle Jolt Debug/Release qualifiés.

- `maximum_friction_force` freine passivement la glissière avec capacité mutable en N, effort signé séparé et priorité des moteurs ; charge, arrêt, contacts, sommeil et oracle Jolt Debug/Release qualifiés.

- Le servo `SliderMotor3D.position` pilote une course cible par ressort amorti physique, force symétrique bornée et cible projetée sur les limites ; mutations, contacts et oracle Jolt Debug/Release qualifiés.

- Le moteur de glissière `SliderMotor3D` pilote une vitesse relative signée avec capacité symétrique en N, freinage à vitesse nulle, effort moteur séparé et mutation sûre.

- Glissière 3D : repères locaux, translation libre sur X, orientation retenue, limites signées facultatives et rigides, mesures de réaction et mutations sûres.

- La charnière suit ensemble un angle et une vitesse avec `HingeMotor3D.position_and_velocity`, ressort physique et bornes symétriques ou signées ; poursuite, mutations et consommateurs qualifiés.

- `HingeLimitSpring3D` rend les butées angulaires souples : raideur/amortissement physiques, mesure signée séparée et mutation sûre, avec butées rigides conservées par défaut. Oscillations, charge, pivot excentré, moteurs et contacts qualifiés face à Jolt en Native Debug/Release.

- Les moteurs de charnière en vitesse et position acceptent des bornes de couple signées : effort asymétrique, unidirectionnel ou imposé, avec budget par pas, mutation et gardes ; constructeurs symétriques conservés.

- `maximum_friction_torque` freine passivement une charnière sans moteur, avec capacité mutable, effort signé séparé et tenue sous charge. Budget du pas, priorité des moteurs, contacts, sommeil et invalidation qualifiés ; trajectoires comparées à Jolt en Native Debug/Release.

- `HingeMotor3D.position` pilote un angle signé par raideur/amortissement explicites et couple borné, avec mutation de cible, modes vitesse/position et butées actuelles. Le resserrement d’une butée unilatérale corrige la pose sans créer de vitesse de récupération.

- `FixedConstraint3D` maintient une pose relative complète, capture l’assemblage courant ou aligne deux repères locaux, mesure force/couple et accepte mutation, suspension et réattache. Chaînes chargées, contacts, sommeil et invalidation testés ; équilibres et mouvements établis comparés à Jolt sur macOS ARM64 Native Debug/Release.

- `HingeMotor3D` motorise une charnière à vitesse relative et couple maximal, avec inversion, arrêt et mesure séparée du couple. L’effort partagé avant déplacement et avec les contacts conserve sa borne ; inertie au pivot, butées et pendule qualifiés face à Jolt en Native Debug/Release.

- `HingeConstraint3D` relie deux ancrages autour d’un axe avec angle zéro local, butées rigides, réactions de force/couple et mutations. Elle partage les contacts et îlots de sommeil de `World3D` ; pendules et butées comparés à Jolt sur macOS ARM64 Native Debug/Release.

- La limite rotationnelle du CCD linéaire est qualifiée contre Jolt : rotation
  seule ou translation parallèle, contact manqué en un pas et trouvé avec
  sous-pas sur les cas testés ; aucune garantie rotationnelle exacte.

- `Plane3D` représente un demi-espace infini sur corps fixe : distance, rayon,
  balayages, appuis convexes, composés mobiles, capteurs et CCD linéaire. La
  sélection des paires ne lui attribue aucune borne finie artificielle.

- Les grilles de hauteurs acceptent un masque de trous par sommet et un choix
  explicite de diagonale. Les triangles survivants restent immuables, orientés
  vers le haut et remplaçables sur un corps fixe ; balayages, chutes, CCD et
  événements respectent les ouvertures et leurs bords réels.

- `Cylinder3D`, `TaperedCylinder3D` et `TaperedCapsule3D` ajoutent des solides
  ronds d’axe local Y : géométrie continue, rayons et balayages, paires obliques,
  caps d’appui, terrains et CCD de translation. Les sections circulaires donnent
  masse, centre et inertie géométriques, y compris cône et sphère contenante.
  Les composés, filtres et mutations acceptent ces nouvelles familles.

- `ShapeCast3D`, `Geometry3D.shape_cast` et `World3D.shape_cast` ajoutent les
  balayages translationnels de capsule, boîte et enveloppe convexe, avec
  poses initiales indépendantes, triangles bilatéraux, identités et filtres.
  Les témoins au contact utilisent la frontière géométrique ; l'orientation
  reste constante et le solveur de simulation conserve son contrat de CCD.

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
