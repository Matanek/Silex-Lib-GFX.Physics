# Créer un assemblage ragdoll et manipuler sa pose

`Ragdoll3DSettings` décrit une hiérarchie réutilisable de corps reliés par
des articulations [swing/twist](SwingTwist3D.md). `World3D.create_ragdoll`
crée une instance indépendante ; `destroy_ragdoll` détruit ses corps et
leurs articulations. Le [consommateur public](../../Tests/Consumer/Tests/Ragdoll3D.sx)
montre les poses, les centres décalés et plusieurs instances.

## Décrire les membres au repos

Ce fragment crée une chaîne de trois membres dans un monde existant `world` :

```sx
let body = Physics.RigidBody3DSettings()
var settings = Physics.Ragdoll3DSettings([
    Physics.RagdollPart3D(-1, body),
    Physics.RagdollPart3D(0, body,
        local_transform:Physics.Transform3D(Math.Vec3(1.0, 0.0, 0.0))),
    Physics.RagdollPart3D(1, body,
        local_transform:Physics.Transform3D(Math.Vec3(0.0, 2.0, 0.0)))
])
var ragdoll = world.create_ragdoll(settings,
    Physics.Transform3D(Math.Vec3(0.0, 10.0, 0.0)))
```

Le premier membre est l’unique racine (`parent = -1`). Les suivants indiquent
un parent déjà présent dans le tableau. `local_transform` place le repère
d’articulation par rapport à son parent ; celui de la racine est relatif au
placement passé à la création. Le tableau initial est copié par les réglages.

`body_offset` place l’origine de la forme par rapport au repère d’articulation.
Il peut contenir une translation et une rotation. Le centre de masse conserve
son propre décalage dans les réglages du corps. `body.transform` doit rester
l’identité : le placement de l’assemblage et `body_offset` possèdent cette
responsabilité.

Le champ `joint` du membre enfant configure ses limites, friction et moteurs.
Les deux repères locaux de cette articulation doivent rester l’identité :
l’assemblage les dérive du repos et des décalages de corps, avec un angle
relatif nul au repos. Chaque liaison doit inclure au moins un corps dynamique.
La racine n’a pas d’articulation parent.

## Lire et imposer une pose

`write_pose(output)` remplace le tableau de sortie par les repères
d’articulation mondiaux, dans l’ordre des membres. `write_local_pose(output)`
conserve la racine **en coordonnées mondiales** et exprime chaque autre
membre relativement à son parent. Les décalages de forme sont exclus de ces
deux poses ; `body(index).transform()` lit la pose mondiale de la forme.

`set_pose(pose, reset_velocity:true)` et `set_local_pose(pose,
reset_velocity:true)` attendent exactement un transform par membre, avec les
mêmes conventions que les lectures. L’imposition efface les cibles cinématiques,
réactions et impulsions mémorisées des articulations de l’assemblage, puis
réveille le monde. Par défaut elle annule les vitesses linéaires et angulaires ;
`reset_velocity:false` les conserve. Elle conserve les forces déjà appliquées.

Une pose imposée est un placement immédiat. Pour suivre une cible avec des
efforts physiques, configurer les moteurs des articulations. Une pose arbitraire
peut dépasser leurs limites ou séparer leurs ancrages ; le solveur reprend
leur résolution au prochain pas positif.

## Collisions et durée de vie

Deux membres directement parent/enfant ne se heurtent pas. Les autres membres
d’une même instance suivent leurs filtres ordinaires ; `self_collision:false`
supprime toutes les collisions internes. Deux instances restent distinctes,
même lorsqu’elles partagent les mêmes réglages. Ce filtrage s’applique aussi
aux capteurs et à la collision continue et se combine avec `CollisionFilter3D`.
Les requêtes géométriques continuent d’utiliser leur propre filtre de requête.

`body(index)` donne accès au corps et `joint(index)` à l’articulation parent,
ou `null` pour la racine. Détruire séparément l’un de ces objets invalide
l’assemblage (`is_valid() == false`). `destroy_ragdoll` peut encore nettoyer
ses corps restants ; un second appel est une erreur. La fin de vie du monde
invalide aussi l’assemblage et tous ses handles, sans que ceux-ci retiennent
le monde.

## Qualification

Les tests couvrent les rotations non commutatives, les décalages de masse,
les poses, le filtrage, les handles périmés et une chute libre à 60/120 Hz.
Le témoin Jolt épinglé compare `Ragdoll.GetPose/SetPose` après conversion
explicite entre origines de corps et repères d’articulation, ainsi que les
paires autorisées dans une instance et entre instances, en Debug/Release.
Cette fondation n’établit pas encore une qualification générale des chutes
avec contacts et poses motorisées d’un ragdoll.
