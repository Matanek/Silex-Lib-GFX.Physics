# Simuler un monde 3D avec plusieurs workers

`World3D` utilise un seul thread par défaut. Pour répartir les travaux physiques
indépendants, appeler `world.enable_parallelism(4)` entre deux pas. Le même monde
peut revenir à un worker par `world.enable_parallelism(1)` ; cette opération
ferme son pool. `world.worker_count()` retourne le nombre configuré.

```sx
use GFX.Physics

func main() {
    var world = Physics.World3D()
    world.enable_parallelism(4)
    world.create_rigid_body()
    world.step(1.0 / 60.0)
    world.enable_parallelism(1)
}
```

Le nombre doit être strictement positif. Réappliquer le nombre courant ne recrée
pas les workers. Chaque monde possède son pool ; sa destruction attend sa fin.
Un pas nul conserve son comportement et ne lance aucun travail.

## Ordre et accès au monde

`step` reste synchrone : ses tâches sont terminées et ses contacts et événements
sont publiés lorsqu'il retourne. Réserver tous les accès au monde et à ses
handles au thread appelant, entre deux pas ; le monde ne constitue pas un
conteneur à mutations concurrentes. Une mutation ou un pas réentrant pendant
la simulation est rejeté.

L'intégration des corps et la géométrie des contacts utilisent des plages
indépendantes. Le solveur de vitesses répartit les contacts et les articulations
sans changer l'ordre des calculs pour chaque corps modifié. L'ordre des points
d'un contact et des lignes d'une articulation reste conservé. Les supports fixes
peuvent être partagés en lecture par les contacts ; les articulations conservent
leurs dépendances sur les deux corps.

Sur une même cible, avec les mêmes sources, build et entrées, les états et les
observations gardent une égalité exacte entre un et quatre workers dans le
[consommateur de qualification](../../Tests/Consumer/Tests/ParallelWorld3D.sx).
Cette garantie n'affirme pas l'identité flottante entre architectures différentes.

## Quand augmenter le nombre de workers

Les petits lots s'exécutent directement. Les longues chaînes liées peuvent
imposer des étapes séquentielles. La préparation du monde, les réveils, les
véhicules, la correction des positions, le CCD et la publication gardent leur
ordre séquentiel. Plusieurs workers ne garantissent donc pas une accélération ;
mesurer la charge représentative sans rendu avant de choisir ce nombre.

Le [témoin interne](../../Tests/ParallelWorkers3D.sx) vérifie la participation
simultanée de quatre exécutions dans les cinq phases réparties. Il est séparé
des mesures de coût : ses rendez-vous servent uniquement à la preuve de concurrence.
