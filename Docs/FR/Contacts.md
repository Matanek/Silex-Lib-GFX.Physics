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

Les formes générales produisent des contacts géométriques et les boîtes/cercle
non arrondis reçoivent la réponse dynamique complète. Les capteurs utilisent
des flux d’événements séparés et n’apparaissent pas comme contacts solides.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Contacts.sx
```
