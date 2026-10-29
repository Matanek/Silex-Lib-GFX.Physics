# Terrains et assemblages de contraintes

Utiliser un [terrain par hauteurs](HeightField3D.md) pour un relief régulier
éditable par versions, un [maillage fixe](Geometry3D.md) pour une surface
triangulée arbitraire, et les contraintes ci-dessous pour assembler les corps.
Les surfaces triangulées conservent leur politique de face avant ; elles
n'acquièrent pas une mobilité dynamique par leur seule construction.

## Choisir une liaison

| Famille | Intention et réglages disponibles |
| --- | --- |
| [Fixe](Fixed3D.md) | conserver la pose relative, avec repères locaux et réactions de force/couple |
| [Point](World3D.md#relier-deux-corps-par-un-point) | réunir deux ancrages en laissant les orientations libres |
| [Distance](World3D.md) | longueur ou plage, ressort en hertz et amortissement |
| [Charnière](Hinge3D.md) | angle signé, butées, ressorts, moteurs et friction à couple borné |
| [Glissière](Slider3D.md) | course signée, butées, ressorts, moteurs et friction à force bornée |
| [Cône](Cone3D.md) | limiter l'ouverture relative ; pas de moteur propre à cette famille |
| [Swing/twist](SwingTwist3D.md) | cône ou pyramide, torsion, moteurs et friction angulaire |
| [Six degrés de liberté](SixDOF3D.md) | axes linéaires et angulaires, limites, ressorts, moteurs et friction |
| [Chemin](Path3D.md) | courbe Hermite ouverte ou bouclée, orientation, moteur et friction |
| [Engrenage](Gear3D.md) | coupler deux rotations par un ratio |
| [Crémaillère](RackAndPinion3D.md) | coupler rotation et translation |
| [Poulie](Pulley3D.md) | longueur pondérée des deux brins, ratio et limites |

Les moteurs et ressorts ne sont pas des options communes à toutes les familles.
Le guide de chaque liaison définit ses unités, repères, bornes d'effort et
mutations. Les collisions entre corps liés restent soumises aux filtres ordinaires :
choisir des formes et ancrages compatibles plutôt que forcer leur chevauchement.

## Terrains qualifiés

Les grilles couvrent espacements distincts, deux diagonales, trous par sommet,
reliefs irréguliers et poses rigides. `with_heights` et `with_holes` créent une
version ; `set_shape` la publie. Les anciens résultats et formes restent sûrs.
La comparaison à un maillage exhaustif conserve faces gagnantes, distances,
normales et balayages pour sept familles de volumes, dont les formes effilées.
Des contrôles analytiques sur une grille de 65 × 65 sommets ajoutent requêtes,
contacts et appui d'un personnage enregistré dans un monde transformé.

Les hauteurs Silex gardent leur précision `float`. Le témoin Jolt 5.6.0 utilise
un heightfield à 16 bits et compare les hauteurs après édition à 0,2 mm près,
les fractions à 5e−5 et les normales à 2e−3. Son édition quantifiée en place
n'est pas le contrat de versions immuables de Silex. Les réglages de compression
ne font pas partie de cette API ; les matériaux se règlent sur les corps.

La sélection de cellules réduit le travail des requêtes locales. Certaines
distances positives et certains parcours CCD restent exhaustifs ; l'édition
construit une version complète. Aucun coût constant ni débit universel n'est garanti.

## Assembler sous charge

Le [consommateur regroupé](../../Tests/Consumer/Tests/TerrainConstraintQualification3D.sx)
complète les témoins isolés des familles par deux assemblages :

| Montage | Observations | Budget de position à 1/60 s |
| --- | --- | --- |
| Deux guides SixDOF et poulie 1:1, masses 2/8 kg, contact au sol | première accélération, longueur, équilibre, tension, mutations et retrait d'un corps | 8 passes |
| Même montage spatial, ancrages hors du plan et ratio 2 | efforts latéraux des guides, tension et longueur pondérée | 48 passes |
| Chemin motorisé portant une charge sur charnière oblique, puis contact avec un mur | erreur d'ancrage, appui, force motrice bornée, inversion et retrait du chariot | 8 passes |

Ces montages utilisent 24 passes de vitesse. Les budgets sont des propriétés
des recettes qualifiées, pas une garantie de précision pour tout assemblage.
Le montage spatial à huit passes dépasse la borne de 1 cm au premier impact
dans les deux moteurs : environ 2,2 cm dans Silex et 3,2 cm dans Jolt. Ce budget
reste hors de la qualification à 1 cm ; la borne est conservée à 48 passes.
Augmenter le budget a un coût à mesurer dans la scène consommatrice.

Les comparaisons Native Debug/Release et Jolt contrôlent 52 observations :
hauteurs, normales, fractions, vitesses, positions, tensions, réactions de guidage,
résidus et résultats du retrait. Les équilibres sont aussi calculés analytiquement.
La réaction verticale du chariot chargé est moyennée sur une seconde : elle
retrouve le poids total de 58,86 N à 1 N près. La phase exacte des impacts
n'est pas une promesse commune aux deux solveurs.

Une mutation Silex efface les réactions devenues incompatibles ; détruire un
corps invalide ses liaisons incidentes et conserve les autres corps. L'oracle
Jolt retire explicitement ses contraintes avant de détruire le corps : il
contrôle les états physiques communs, sans simuler les mêmes handles publics.

## Rejouer les preuves

Depuis la racine du workspace, ou la racine du groupe de Spec qui contient les
mêmes chemins :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/TerrainConstraintQualification3D.sx --backend native
python3 Silex-Benchmarks/Sources/Physics3D/TerrainConstraintsRun.py --mode both
```

Le second outil requiert le dépôt de benchmarks et les bibliothèques Jolt
épinglées préparées par son harnais principal. Il contrôle les sources, la
résolution des packages, les configurations et les champs de sortie ; ses
autotests refusent les champs manquants, dupliqués ou non finis et perturbent
chaque observation. Cette qualification fonctionnelle ne remplace pas une
campagne globale de performance, de parallélisme ou de déformables.
