# Corpus de reconstruction et budgets

Ce contrat fixe les preuves de la reconstruction Silex native. Chaque résultat
nomme OS, architecture, CPU, commits, mode, workers, pas fixe et répétitions.
Les budgets de temps et mémoire appartiennent uniquement à la machine macOS
ARM64 de référence ; ils ne prédisent pas les résultats x64.

La correction s’exécute en Debug et Release. Les mesures Release utilisent un
échauffement puis sept processus isolés et publient médiane, étendue et écart
absolu médian. La correction est un garde-fou dur : aucune accélération ne
justifie un confinement, recouvrement, état fini ou déterminisme invalide.

## Scènes partagées

Le corpus couvre une chute de référence, des scènes clairsemées de 1 000,
5 000 et 10 000 boîtes, une pile de 1 000 boîtes et des conteneurs de 1 800 et
5 000 cercles. Chaque scène fixe dimensions, ordre initial, matériaux, gravité
et pas. Silex n’a pas à reproduire les bits flottants de Box2D.

## Comparer directement les performances à Box2D

Lancer `Corpus2D.sx` avec `--box2d-parity` pour comparer les moteurs.
Ce mode fixe la gravité à −10 m/s² (zéro dans les scènes clairsemées), la
raideur de contact à 30 Hz et la masse de chaque corps dynamique à 1 kg.
Les scènes clairsemées et de cercles désactivent le sommeil du monde et des
corps. Sans cette option, le corpus conserve ses anciens réglages Silex pour
les non-régressions historiques ; leurs temps ne sont pas comparables directement.

Après un échauffement de chaque exécutable, alterner sept processus par moteur
sur la même machine disponible, en Release et avec les mêmes sous-pas et workers.
Conserver les sorties mesurées, sans l'échauffement, puis exécuter :

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CompareCorpus.py box2d.log silex.log
```

Ce contrôle exige le marqueur de charge `box2d-3.1.1-v1`, des configurations
équivalentes, les invariants physiques, le déterminisme de chaque moteur et
une MAD au plus égale à 5 %. Il rapporte le ratio des médianes Silex/Box2D et
échoue au-dessus de 1. Des étendues temporelles qui se chevauchent empêchent
également de conclure positivement : affiner alors la campagne, sans transformer
le bruit en ralentissement autorisé. Le contrôle compare une configuration par
scène et par invocation ; il ne remplace ni l'audit des sources et options de
compilation, ni le corpus différentiel complet.

Cette porte ne prouve que les configurations mesurées. Le témoin Box2D accepte
un, deux et quatre workers grâce à son adaptateur de tâches du benchmark ; les
comparaisons parallèles exigent donc aussi des nombres égaux. Atteindre un
budget absolu ci-dessous ne prouve pas la parité de performance.

## Budgets historiques de non-régression

Sur la machine de référence, les budgets vont de 4 ms par pas pour 1 000 corps
clairsemés à 33,33 ms pour 10 000 corps ou la pile. Les scènes de cercles visent
16,67 ms. Une médiane qui régresse de plus de 5 % ou une dispersion supérieure
à 5 % échoue même sous le plafond absolu.

La mémoire mesure le RSS du processus séparément du temps. Après soustraction
de la scène de référence appariée, chaque corps dynamique clairsemé dispose de
1 Kio ; une scène dense ajoute 512 octets par paire persistante. Ces plafonds
ne sont pas des cibles d’allocation.

## Sentinelles GFX

Boids2D protège le débit 2D, WorldRendering3D impose au moins 120 FPS sur sa
configuration de référence, et ShapeGallery2D vérifie construction, texte,
renderer et diagnostics. Le smoke automatique ne remplace pas l’acceptation
visuelle explicitement demandée. Aucune capture automatisée n’appartient à ces
gates.

Les résultats bruts sont datés sous `Benchmarks/Baselines/` avec les commits
exacts. Remplacer une baseline exige corpus vert, variance admissible et revue
explicite de chaque gate modifié.

## Qualification des chenilles 3D

Le runner `Silex-Benchmarks/Sources/Physics3D/TrackedGroundRun.py` compare Jolt
5.6.0 épinglé et le SDK Silex Native Debug/Release sur macOS ARM64, un worker,
un sous-pas et 12/4 itérations, à 60/120 Hz. Seize recettes en vol produisent
5 792 états par moteur/mode ; six au sol en produisent 8 652. Chaque recette
sol dure 2 s de réception freinée, 2 s de conduite puis 4 s de freinage.
Une perturbation Jolt de hauteur initiale de 1 micromètre vérifie le conditionnement.

Les bornes pointwise du châssis restent 0,05 m, 0,1 m/s, 0,02 rad et 0,15 rad/s.
Les bilans par pas acceptent 0,1 N·s et 0,1 N·m·s ; angles de roue à
0,0001 rad, vitesses angulaires à 0,0001 rad/s et régime à 0,02 RPM. Sur fenêtres de 1 s alignées avec les
commandes, efforts résultants sont bornés à 20 N et 30 N·m, charges normales
moyennes par roue à 20 N, incréments de rotation à 0,1 rad. La récupération
exige six appuis de 163,5 N, 981 N au total, hauteur 0,88365 m et vitesse sous
0,05 m/s. L’absence d’adhérence garde le châssis immobile malgré les bandes.

Le partage des efforts tangentiels entre six contacts n’est pas unique : sa
parité individuelle n’est pas revendiquée. Le miroir gauche/droite conserve
poses pointwise, mais compare les vitesses moyennes sur 1 s aux mêmes bornes,
car l’ordre des contacts Jolt dépasse 0,1 m/s ponctuellement. La comparaison
principale Silex/Jolt reste entièrement pointwise. Jolt garde une ancienne
vitesse de roue sans appui ; le SDK publie la vitesse finale de bande. Les
vérifications respectent chacune de ces frontières et conservent les bruts.
Les textes flottants des deux moteurs sont relus comme binary32.

632 corruptions sont rejetées sur les deux modes et moteurs. Le rapport contient
les hashes de sorties et les écarts ; Debug/Release sont bit-identiques dans
ces recettes. La qualification porte sur les bandes idéales, contacts rayon
et plan décrits. Les maillons articulés, les autres terrains et les budgets
de FPS restent hors de cette campagne.

## Qualification de l’équilibre moto

`Silex-Benchmarks/Sources/Physics3D/MotorcycleReferenceRun.py` qualifie la
référence Jolt 5.6.0 épinglée ; `MotorcycleRun.py` compare son consommateur
public Silex. Seize recettes de 4 s à 60/120 Hz produisent 11 552 états par
moteur/mode, un worker, un sous-pas et 12/4 itérations configurées, Native
Debug/Release sur macOS ARM64. Le châssis de 100 kg a une inertie isotrope de
100 kg·m², deux roues de rayon 0,3 m à ±1 m, course 0,2–0,6 m, ressorts
10000 N/m et amortissement 1000 N·s/m. Le couple moteur est nul. Les virages
partent à 5 m/s, les directions en vol à ±20 m/s. L’adhérence des virages vaut
1/0,15 ; les autres recettes n’ont pas d’adhérence tangentielle.

Les budgets châssis pointwise sont 0,05 m / 0,1 m/s / 0,02 rad / 0,15 rad/s.
La comparaison de chute sans assistance s’arrête pointwise au premier centre
sous 0,2 m dans l’un des moteurs, puis exige la chute et un état borné ;
11 009 états restent comparés pointwise. Le filtre de pente Silex est local à
la suspension ; `pi/2-1e-6` sur ce plan conserve les mêmes contacts que le
filtre Jolt relatif à la verticale monde. Les autres défauts restent inchangés.

Les contrôles indépendants recomposent la cible depuis les efforts précédents,
la limite de direction, le couple PID et la compensation de vitesse aux roues.
Bornes : 3e-6 rad de direction, 3e-4 de distance de cible, 0,1 N·m·s d’impulsion
PID, 0,005 N·s de bilan linéaire et 3e-5 m de position par pas. La référence
instrumentée vérifie aussi 3e-6 m/s de compensation et la décroissance intégrale
par appel solveur. Ses 19 gardes et les 16 gardes du consommateur rejettent les
corruptions par mode. Les sorties Native Debug/Release sont identiques.

Les coefficients géométriques du ressort restent fixés pour tout le pas,
y compris les visites de résolution après intégration de pose. Le lissage
reste par pas ; la décroissance intégrale suit les appels effectifs du
solveur, dont le nombre peut différer entre Jolt et Silex. La parité porte sur
les observations physiques, sans exiger l’identité de ces caches privés.
L’assistance est un actuateur externe sans réaction opposée au support. Cette
campagne couvre le plan à rayons, l’équilibre et les virages sur élan ; elle
ne qualifie pas encore la propulsion composée, tous les détecteurs ou terrains,
ni un coût CPU/GPU. Rapport : `motorcycle-qualification.json` dans le cache
`.silex/physics3d-oracle/` du groupe ou workspace.

La convention signée des roues Silex est conservée : la limite porte sur
l’amplitude, même avec un angle maximal négatif ou un axe inversé. Ces cas sont
vérifiés analytiquement. Le contrôleur Jolt épinglé laisse ces représentations
contourner sa limite ; les recettes de parité emploient les conventions
positives de Jolt.
