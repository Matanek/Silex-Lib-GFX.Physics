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

Le monde conserve les paires candidates proches et rafraîchit leur manifold.
Chaque `Contact2D` nomme les deux colliders exacts et leurs corps,
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
conserve un contact par paire exacte de colliders, indépendamment de leur ordre
de création. Les ancres du solveur restent relatives au centre de masse : celles
des formes orientées suivent la rotation, tandis que l’ancre d’un cercle reste
invariante. Un corps composé à centre de masse décalé peut ainsi tourner ou
changer de cible cinématique sans perdre le contact du plancher.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/DynamicShapes.sx
silex test Packages/GFX.Physics/Tests/Consumer/Tests/ContactSnapshots.sx
```

## Contacts prédictifs

Une paire peut produire un manifold jusqu’à une séparation positive de 0,02 m.
Pour une face inclinée, ses deux extrémités découpées sont conservées : l’une
peut dépasser cette marge tandis que l’autre touche déjà le support.
Le solveur peut ainsi freiner une approche avant pénétration, même lorsque le
CCD est désactivé. Un événement de début correspond à l’apparition du manifold,
pas nécessairement au toucher géométrique. Un événement d’impact exige une
vitesse d’approche strictement supérieure à `hit_event_threshold` et une
impulsion normale effectivement accumulée sur ce point pendant le pas.
Un rapprochement sans impulsion n’est donc pas un impact.

La fréquence effective de contact est plafonnée à un huitième de l’inverse
de la durée du sous-pas ; elle est ensuite doublée pour une surface statique.
Les accesseurs gardent la fréquence configurée. Les snapshots conservent la
séparation du manifold préparé au début du pas, y compris pour les cercles.

Le [témoin prédictif](../../Benchmarks/SpeculativeContactsOracle2D.sx) compare
1 536 observations de cercle/cercle, boîte/boîte, capsule/capsule et
segment/capsule : deux durées de pas, un ou quatre sous-pas, approches sous et
au-dessus de la marge, repos et seuil exact d’impact. Le CCD est désactivé pour
isoler la réponse prédictive. Ces cas ne constituent pas une preuve universelle
pour toute forme, vitesse ou scène.

Le [témoin géométrique](../../Benchmarks/GeometryOracle2D.sx) vérifie aussi quatre
faces prédictives inclinées, dont une partiellement hors du support.
