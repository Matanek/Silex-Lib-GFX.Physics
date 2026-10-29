# Personnage virtuel enregistré

`VirtualCharacter3D` combine le [contrôleur de capsule](Character3D.md) et une
présence cinématique dans le monde. Les autres personnages et les requêtes
ordinaires voient cette capsule ; le contrôleur exclut sa propre présence.

Ce fragment suppose un monde `world`, une vitesse `velocity` et une durée
`delta` déjà définis.

```sx
var character = world.create_virtual_character(
    Physics.CharacterMover3DSettings() ..max_push_force = 100.0,
    Math.Vec3(0.0, 0.852, 0.0))
var result = character.move(world, velocity.multiply(delta), delta)
velocity = result.clip_velocity(velocity)
```

Le personnage possède sa position, accessible par `position()`. `move` met à jour
sa capsule une fois ; le pas du monde ne rajoute pas son déplacement. Le corps
cinématique reste à vitesse nulle, comme une présence à pose contrôlée. `mass`
transmet le poids et `max_push_force` borne la poussée du contrôleur ; les corps
physiques conservent leurs réactions ordinaires contre la présence cinématique.
Le [mode physique](PhysicalCharacter3D.md) sert aux personnages qui doivent
recevoir le recul et participer au solveur par leur propre masse dynamique.

`is_grounded()`, `ground_normal()`, `support()`, `contact_count()` et `contact(index)`
décrivent le dernier mouvement. Une durée nulle conserve la pose et les contacts.
`try_resize(world, capsule)` conserve les pieds et refuse un chevauchement ;
`set_position(position)` téléporte et oublie l’ancien support. `body()` fournit
la présence pour les requêtes et les attaches. Garder une capsule verticale et
confier son déplacement au personnage pour conserver l’autorité des poses.

Le troisième argument de `create_virtual_character` est le `CollisionFilter3D`
de sa présence. Catégories, masques réciproques et groupes s’appliquent aux
rencontres ; le filtre de requête de CharacterMover3DSettings conserve son rôle
pour la sélection des obstacles et l’observation des capteurs.
Les rencontres virtuel/virtuel suivent l’ordre des appels à `move`, comme toute
mise à jour séquentielle de personnages pilotés. Les contacts identifient les
pairs par leurs handles de corps ordinaires.

Le monde possède le corps. `destroy_virtual_character(character)`, le retrait
direct de son corps ou la fin du monde invalide le handle. `move` et `try_resize`
refusent un monde étranger. Le [mover seul](Character3D.md) reste disponible
lorsqu’aucune présence de personnage n’est souhaitée dans les requêtes du monde.

[Consommateur des interactions](../../Tests/Consumer/Tests/CharacterInteractions3D.sx) :
présence, requêtes, absence de double intégration, trois combinaisons de modes,
masques, pause et durées de vie.
