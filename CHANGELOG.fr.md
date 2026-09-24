# Journal des versions de GFX.Physics

Ce journal commence à 0.7.0 et couvre les changements depuis le tag 0.6.0.
Les changements futurs sont consignés sous `## [Unreleased]` avant publication,
puis traduits dans `CHANGELOG.md`.

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
