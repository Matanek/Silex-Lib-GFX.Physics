# Collisions de cartes tuilées

`Physics.TileMapCollider2D` est un composant ECS à ajouter à une entité portant
`Scene2D.TileMap` et `Scene2D.Transform`. Installer `Plugins.Physics2D`, puis :

```sx
world.spawn(ECS.EntityRecipe()
    ..with(Scene2D.Transform())
    ..with(map)
    ..with(Physics.TileMapCollider2D()))
```

Chaque cellule occupée est solide, quel que soit son indice graphique. Garder
les décorations, pièces et dangers dans des couches séparées. Le composant
accepte un `collision_filter` à la construction. Il possède le
`PhysicsBody2D` généré sur cette entité : ne pas en ajouter un autre.

Les suites horizontales de cellules sont fusionnées, puis les suites de même
largeur et de même colonne sont réunies entre lignes successives. La construction
parcourt la grille en temps linéaire et conserve les trous. Une carte pleine
produit un corps fixe et un seul collider, sans entité par tuile. Les rectangles
sont convertis en mètres avec `scene_units_per_meter` du plugin. La translation
et la rotation sont permises ; l'échelle globale doit rester `(1, 1)`.

Le plugin reconstruit les formes lorsque le contenu ou le filtre change, avant
la réconciliation des corps dans `post_update`. Les frames stables ne parcourent
pas les cellules et conservent l'identité du corps. Une édition faite pendant un
callback physique est prise en compte à la frame suivante. Une reconstruction
remplace le corps : ne pas conserver ses handles au-delà d'une édition.
`enable(false)` suspend le corps ; retirer le composant, la carte, son transform
ou l'entité détruit les collisions. Une carte vide n'a aucune forme implicite.
La visibilité graphique n'affecte pas les collisions.

Pour un monde physique autonome, `collider.body(map, scene_units_per_meter)`
retourne la recette `PhysicsBody2D`, et `collider.rectangles(map)` donne les
rectangles en coordonnées de cellules (`column`, `row`, `columns`, `rows`).
La fusion couvre des rectangles pleins : pentes, surfaces à sens unique et
collisions partielles par tuile restent hors de ce contrat. Modifier une cellule
reconstruit actuellement les collisions de toute la carte ; découper les très
grands mondes éditables en plusieurs couches/cartes avant de viser du streaming.

[Retour à GFX.Physics](README.md)
