# Contacts persistants du monde

Après chaque `World2D.step`, les contacts solides sont accessibles comme
snapshots en lecture seule, ordonnés par identité stable des colliders.

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)

for contact in contacts {
    let first = contact.first_collider()
    let second = contact.second_collider()
    let manifold = contact.manifold()
    print("$(manifold.point_count()) $(contact.normal_impulses().count())")
}
```

Le monde conserve les paires tant que les formes se touchent et rafraîchit leur
manifold. Chaque `Contact2D` nomme les deux colliders exacts et leurs corps,
contient une impulsion normale et tangentielle par point, la friction et la
restitution résolues, ainsi que son état actif. Les surcharges de
`write_contacts` acceptent un `RigidBody2D` ou un `Collider2D` avant le buffer
pour filtrer sans allocation.

Ces snapshots sont des valeurs autonomes du pas terminé. Après destruction
d’un collider nommé par un événement copié, sa géométrie, son matériau et son
identifiant applicatif restent lisibles dans `pair()`. Son handle devient
invalide et toute mutation par ce handle échoue, sans pouvoir atteindre un
collider recyclé.

Cercles, capsules, segments, polygones convexes ou arrondis et segments de
chaîne rejoignent le même graphe Soft Step. Le manifold conserve jusqu’à deux
points compatibles avec le warm start ; friction, restitution, convoyeur et
résistance au roulement proviennent des colliders effectivement touchés. Une
chaîne reste fixe et unilatérale, avec son matériau propre à chaque segment.
Les capteurs utilisent des flux d’événements séparés et n’apparaissent pas
comme contacts solides. `write_sensor_overlaps(output)` écrit tous les overlaps
courants ; `write_sensor_overlaps(sensor, output)` sélectionne un capteur.

Quand plusieurs colliders des deux mêmes corps se touchent à un coin, le monde
retient le manifold le plus pénétrant au lieu de dépendre de leur ordre de
création. Les ancres du solveur restent relatives au centre de masse : celles
des formes orientées suivent la rotation, tandis que l’ancre d’un cercle reste
invariante. Un corps composé à centre de masse décalé peut ainsi tourner ou
changer de cible cinématique sans perdre le contact du plancher.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/DynamicShapes.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContactSnapshots.sx
```
