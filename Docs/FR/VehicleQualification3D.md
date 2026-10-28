# Profils qualifiés des véhicules 3D

Les voitures, chenillés et motos utilisent le même monde de corps rigides. Le
monde avance suspensions, contacts, pneus et transmission à chaque pas ; les
commandes restent actives jusqu’à leur remplacement. Ces modèles fonctionnent
sans rendu et alimentent les scènes existantes de `Silex-Examples`.

| Véhicule | Modèle et réglages | Profils de conduite observés |
| --- | --- | --- |
| Voiture | [Roues suspendues](VehicleSuspension3D.md), [pneus et freins](VehicleControls3D.md), [moteur et boîte](VehiclePowertrain3D.md) | Départ, virages miroirs, freinage, marche arrière, pente, saut et reprise d’appuis |
| Chenillé | [Deux bandes idéales](TrackedVehicle3D.md), moteur et boîte communs | Virage par vitesses relatives, pivot, freinage, boîte automatique, rampe, supports mobiles et conduite prolongée |
| Moto | [Deux roues et assistance réglable](Motorcycle3D.md), propulsion arrière | Équilibre, braquage limité selon la vitesse, assistance désactivable, accélération/freinage, rampe, envol et réception |

La suspension commune accepte des coefficients SI, une fréquence avec taux
d’amortissement ou des coefficients normalisés à la masse, une précharge et un
point local optionnel d’application des forces. Les voitures peuvent aussi
utiliser des [barres anti-roulis](VehicleAntiRoll3D.md) et une
[limite d’inclinaison](VehicleTiltLimit3D.md). Les forces au contact transmettent
la propulsion et réagissent sur un support dynamique.

## Choisir les contacts et le pas

Le rayon est le défaut. La sphère donne une portée autour des arêtes ; le
cylindre représente la largeur et l’orientation de la roue. Les trois familles
ont des témoins de contact sur boîte horizontale/inclinée, arête, maillage à deux
triangles, grille de hauteurs et support libre de masse finie. Ces parcours
isolent la suspension en coupant propulsion et adhérence tangentielle.

La conduite composée sur plan fixe est qualifiée à 60/120 Hz, 12 itérations de
vitesse et 4 de position, avec un worker et sans sous-pas supplémentaires. Les
profils rayon/sphère enchaînent accélération, virages opposés, friction du sol
réglée à zéro puis restaurée, freinage, marche arrière et arrêt. Voiture et moto
utilisent des courbes de pneus variables ; les chenilles gardent leurs bandes
idéales. Les bilans incluent la compensation linéaire de l’assistance moto.

La conduite chenillée prolongée dispose d’un profil distinct à 48/4 itérations.
Le profil 12/4 reste hors du budget de rectitude sur ce trajet ; augmenter les
itérations fait partie de la configuration qualifiée et ne change pas le défaut
du monde. Aucune garantie pour toute combinaison de réglages ou de terrains
n’est déduite de ces témoins.

## Limites des cylindres larges

Le contact d’un cylindre rigide sur un plan peut former une ligne. Le point
numérique retenu sur cette ligne influence le couple. Dans la conduite composée,
Jolt lui-même dépasse les budgets de trajectoire sous une translation commune
de 0,1 mm du véhicule et du sol, ou sous des commandes miroirs.
La parité complète de ces trajectoires cylindriques reste non qualifiée ;
les contrôles de géométrie, d’adhérence et d’impulsion restent actifs.

La moto équipée de cylindres de 0,4 m de largeur conserve aussi une oscillation
près de l’arrêt dans les deux moteurs : sa vitesse peut encore atteindre
0,28 m/s aux arrêts mesurés. Ce profil ne prouve pas le repos sous 0,05 m/s.
Utiliser les contacts rayon ou sphère pour le profil de conduite moto qualifié
jusqu’à l’arrêt. La géométrie cylindrique ne fournit pas à elle seule un modèle
de pneu déformable.

## Possession et observations

Chaque véhicule possède un seul châssis enregistré dans son monde. Détruire la
façade, son châssis ou le monde invalide les handles existants ; une nouvelle
instance ne réactive pas les anciens handles. `is_valid()` permet de vérifier
leur état. Détruire un support enlève les appuis des observations suivantes.
Un snapshot déjà lu garde ses valeurs et son handle de support, devenu invalide :
vérifier `is_valid()` avant de réutiliser ce handle.

Une modification des commandes ou des réglages du véhicule réveille l’instance concernée. Un corps désactivé
garde sa pose et ses observations ; `step(0)` ne recalcule pas la physique.
Les tests publics mélangent les trois familles et plusieurs ordres de libération
et de réutilisation des emplacements :
[consommateur mixte](../../Tests/Consumer/Tests/VehicleFleet3D.sx).

Les mesures sont exécutées en Native Debug/Release sur macOS ARM64. Elles ne
constituent pas une mesure de FPS, une qualification multiworkers ou une preuve
d’exécution sur les autres plateformes. Les scénarios, variantes de référence
et budgets sont détaillés dans [les preuves de comparaison](OracleAndBudgets.md).
