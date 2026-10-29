# Choisir et vérifier un personnage 3D

Le mode virtuel sert au déplacement contrôlé avec glissement, marches et suivi
du sol. Le mode physique sert à une capsule de masse réelle qui reçoit les
impacts et réagit au solveur. Les deux peuvent partager le même monde.

| Intention | Virtuel | Physique |
| --- | --- | --- |
| Déplacement | `move` calcule et applique une translation pilotée | `set_linear_velocity`, puis `world.step` |
| Présence et contacts avec les autres personnages | `VirtualCharacter3D`, capsule cinématique enregistrée | `PhysicalCharacter3D`, capsule dynamique enregistrée |
| Requête sans présence | `CharacterMover3D.calculate_move` | Requêtes ordinaires du monde |
| Pentes, murs, plafonds | Glissement et pente maximale du mover | Contacts rigides et classement de l’appui après le pas |
| Marches et suivi descendant | Franchissement et `floor_snap` | Réaction physique ; pas de franchissement automatique |
| Poussée d’objets | Force maximale, masse effective au point de contact | Échange de quantité de mouvement par la masse dynamique |
| Poids sur un support | Masse virtuelle, impulsion de gravité séparée | Gravité du corps dynamique |
| Support en translation ou rotation | Transport par les poses successives du support | Contacts, frottement et vitesse de l’appui au point de contact |
| Changement de capsule | Pieds conservés, refus atomique en cas de pénétration | Pieds et masse conservés ; tolérance de pénétration explicite |
| Téléportation | `set_position` oublie l’ancien support | `set_position` efface l’état d’appui précédent |
| Rotation | Capsule verticale du mover | Rotations physiques verrouillées, translations libres |
| Durée nulle | Pose, appui et contacts conservés, aucune impulsion | Aucun pas ni actualisation des contacts |

Les commandes, le saut, la caméra et l’animation appartiennent à l’application.
Un ragdoll articulé reste une autre représentation physique ; ces contrôleurs
ne calculent pas une marche procédurale ou un équilibre animé.

## Ordre dans le pas fixe

Pour un personnage physique, fournir la vitesse voulue avant `world.step(delta)`
et lire son appui après le pas. Pour un virtuel, appeler `move` une fois par pas
et conserver sa position retournée ; ne pas déplacer ensuite son corps comme
un second contrôleur. Le mouvement de plateforme consommé par le mover provient
des poses successives déjà connues : ne pas ajouter sa vitesse à la translation.

Avec le plugin GFX, `Physics3DStep.before_step` et `after_step` donnent ces deux
points d’insertion. Le monde est la ressource `Physics.World3D`. L’application
peut ensuite recopier la position du personnage dans le transform de son visuel.
Le [consommateur intégré](../../Tests/Consumer/Tests/CharacterApplication3D.sx)
vérifie les deux modes, le pas fixe, la pause/reprise et la fin de vie du monde.

Les opérations de mouvement empruntent le monde : elles acceptent aussi la
ressource monde de GFX sans copie ni transfert de propriété.

## Preuves et différences avec Jolt

Le programme indépendant `Silex-Benchmarks/Sources/Physics3D/CharacterRun.py`
compare Jolt 5.6.0 épinglé et le consommateur Silex en Native Debug et Release :
poussée faible, poussée plafonnée, poids virtuel, collision 70/30 kg, chute/repos et
redressement refusé sous plafond. Les seuils absolus sont 0,0001 pour les mesures
de vitesse, changement de capsule et masse, et 0,005 pour le repos.
Les bilans analytiques contrôlent aussi les deux moteurs.

Les [tests du mover](../../Tests/Consumer/Tests/CharacterMover3D.sx), du
[terrain triangulaire](../../Tests/Consumer/Tests/CapsuleTerrain3D.sx), des
[convexes](../../Tests/Consumer/Tests/CharacterConvex3D.sx), de la
[capsule mutable](../../Tests/Consumer/Tests/CharacterResize3D.sx), des
[échanges dynamiques](../../Tests/Consumer/Tests/CharacterDynamics3D.sx), du
[mode physique](../../Tests/Consumer/Tests/PhysicalCharacter3D.sx) et des
[rencontres](../../Tests/Consumer/Tests/CharacterInteractions3D.sx) couvrent les
autres parcours, filtres, retraits et garanties de durée de vie.

Silex partage le budget de poussée entre les enfants d’un même corps composé ;
ce choix empêche de multiplier la force en ajoutant des enfants. Il ne prétend
pas reproduire le budget par contact de Jolt. Le virtuel enregistré correspond
à la présence `mInnerBodyShape` de Jolt : les corps physiques rencontrent un
obstacle cinématique, tandis que les autres virtuels suivent l’ordre des appels.
Le support virtuel est sondé même avec une translation nulle ; dans le témoin
Jolt, une vitesse descendante commune établit d’abord le contact effectif.

La récupération de pénétration du mover reste bornée en nombre de passes.
Le cas d’inclusion profonde dans une boîte isolée est couvert ; un ensemble d’obstacles
incompatibles ne garantit pas une sortie. Les mesures comparatives concernent
le profil natif macOS ARM64 exécuté, pas une campagne de performance ou une
qualification générale de tous les assemblages du solveur.

Voir les guides du [mover](Character3D.md), du
[virtuel enregistré](VirtualCharacter3D.md) et du
[personnage physique](PhysicalCharacter3D.md).
