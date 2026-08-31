# Requêtes spatiales du monde

`World2D` interroge directement ses colliders vivants sans exposer les proxies
ni l’ordre de son accélération spatiale. Les variantes `write_*` remplacent le
contenu d’un buffer appartenant à l’appelant et retournent des statistiques de
parcours. Les variantes `*_any` répondent dès le premier hit logique et les
variantes `*_closest` retiennent la fraction la plus proche.

```silex
var overlaps:Physics.Collider2D[] = []
let stats = world.write_aabb_overlaps(
    Physics.AABB2D(Math.Vec2(4.0, 2.0), Math.Vec2(1.0)),
    overlaps,
    Physics.QueryFilter2D(mask_bits:0x4)
)

var casts:Physics.WorldCastResult2D[] = []
world.write_ray_casts(
    Physics.Ray2D(Math.Vec2(), Math.Vec2(10.0, 0.0)),
    casts
)
var closest = world.ray_cast_closest(
    Physics.Ray2D(Math.Vec2(), Math.Vec2(10.0, 0.0))
)
```

Les recouvrements acceptent une `AABB2D` ou un `ShapePlacement2D`. Les casts
de forme acceptent en plus la translation et une fraction maximale. Tous les
résultats `all` suivent l’identité de création des colliders, indépendamment de
leur position, d’une compaction interne ou du nombre de workers. Un
`WorldCastResult2D` expose point, normale et fraction ; `collider()` n’est
valide que lorsque `hit` vaut `true`.

`QueryFilter2D` est distinct de `CollisionFilter2D`. Ses catégories et son
masque sélectionnent les catégories de colliders sans créer ni modifier une
paire de contact. Les corps désactivés sont absents des requêtes.

Un `Collider2D` fournit `test_point`, `ray_cast_local`, `world_aabb`,
`closest_point` et les propriétés de masse de sa propre géométrie. Un
`RigidBody2D.world_aabb()` réunit les bornes de tous ses colliders. Les handles
conservés dans un résultat deviennent invalides si leur collider est détruit.

Les requêtes sont interdites pendant `step`. Plusieurs lectures peuvent
partager un monde au repos : chaque appel possède ses temporaires et le buffer
reste la propriété du consommateur. `WorldQueryStatistics2D` décrit le nombre
de colliders visités, de candidats AABB et de hits ; il ne révèle aucun détail
de stockage.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/WorldQueries.sx
```

Le témoin différentiel Box2D 3.1.1 couvre AABB, overlap de forme, ray cast,
shape cast et requêtes locales de collider. L’AABB Silex décrit la géométrie
exacte ; Box2D ajoute 2 cm de marge de broad phase dans `b2Shape_GetAABB`,
différence explicitement tolérée par le comparateur.
