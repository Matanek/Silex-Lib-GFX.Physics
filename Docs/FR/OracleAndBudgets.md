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

Cette porte ne prouve que les scènes mesurées. Le benchmark Box2D reste
mono-worker ; la parité multi-worker n'est pas encore couverte. Atteindre un
budget absolu ci-dessous ne prouve pas la parité de performance.

## Budgets historiques de non-régression

Sur la machine de référence, les budgets vont de 4 ms par pas pour 1 000 corps
clairsemés à 33,33 ms pour 10 000 corps ou la pile. Les scènes de cercles visent
16,67 ms. Une médiane qui régresse de plus de 5 % ou une dispersion supérieure
à 5 % échoue même sous le plafond absolu.

La mémoire mesure le RSS du processus séparément du temps. Après soustraction
de la scène de référence, `sparse-10000` dispose de 1 Kio par corps dynamique ;
`circle-5000` ajoute 512 octets par paire persistante. Ce plafond n’est pas une
cible d’allocation.

## Sentinelles GFX

Boids2D protège le débit 2D, WorldRendering3D impose au moins 120 FPS sur sa
configuration de référence, et ShapeGallery2D vérifie construction, texte,
renderer et diagnostics. Le smoke automatique ne remplace pas l’acceptation
visuelle explicitement demandée. Aucune capture automatisée n’appartient à ces
gates.

Les résultats bruts sont datés sous `Benchmarks/Baselines/` avec les commits
exacts. Remplacer une baseline exige corpus vert, variance admissible et revue
explicite de chaque gate modifié.
