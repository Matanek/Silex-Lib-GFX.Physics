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
et pas. L’oracle Box2D reste diagnostique ; Silex n’a pas à reproduire ses bits.

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
