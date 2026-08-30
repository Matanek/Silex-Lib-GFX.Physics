# Contacts persistants du monde

Après chaque `World2D.step`, les contacts solides sont accessibles comme
snapshots en lecture seule, ordonnés par identité stable des corps.

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)

for contact in contacts {
    let first = contact.first_body()
    let second = contact.second_body()
    let manifold = contact.manifold()
    print(manifold.point_count())
}
```

Le monde conserve les paires tant que les formes se touchent et rafraîchit leur
manifold. Les handles des corps restent valides tant que leurs corps existent ;
les snapshots ne donnent jamais accès au cache d’impulsions ni aux structures
du broad phase.

Cercles, capsules, segments, polygones convexes ou arrondis et segments de
chaîne rejoignent le même graphe Soft Step. Le manifold conserve jusqu’à deux
points compatibles avec le warm start ; friction, restitution, convoyeur et
résistance au roulement proviennent des colliders effectivement touchés. Une
chaîne reste fixe et unilatérale, avec son matériau propre à chaque segment.
Les capteurs utilisent des flux d’événements séparés et n’apparaissent pas
comme contacts solides.

Quand plusieurs colliders des deux mêmes corps se touchent à un coin, le monde
retient le manifold le plus pénétrant au lieu de dépendre de leur ordre de
création. Les ancres du solveur restent relatives au centre de masse : celles
des formes orientées suivent la rotation, tandis que l’ancre d’un cercle reste
invariante. Un corps composé à centre de masse décalé peut ainsi tourner ou
changer de cible cinématique sans perdre le contact du plancher.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/DynamicShapes.sx
```
