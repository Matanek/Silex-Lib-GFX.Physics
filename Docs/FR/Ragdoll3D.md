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
efforts physiques, utiliser les commandes de pose motorisée ci-dessous. Une
pose arbitraire peut dépasser leurs limites ou séparer leurs ancrages ; le solveur reprend
leur résolution au prochain pas positif.

## Suivre une pose avec des moteurs

`drive_to_pose(pose, maximum_torque, stiffness, damping)` et
`drive_to_local_pose(pose, maximum_torque, stiffness, damping)` reprennent les
conventions de lecture mondiale et locale. Le tableau doit contenir un transform
par membre. Seules les rotations relatives des enfants deviennent des cibles :
la position et la rotation mondiales de la racine, ainsi que toutes les
translations, ne commandent aucun déplacement. Les corps restent reliés par
leurs ancrages physiques.

L'appel remplace les moteurs de torsion et de swing de chaque articulation,
réveille les corps et efface leurs réactions mémorisées. Il conserve leurs
poses, vitesses, limites, friction et filtres de collision. Le solveur borne les
cibles aux limites articulaires existantes. Les décalages de corps et les
repères actuels des articulations participent à la conversion des rotations.
Les valeurs sont copiées : modifier ensuite le tableau ne change pas la cible.

`maximum_torque` est un couple fini, positif ou nul, en N·m **par axe** ;
`stiffness` est une raideur finie strictement positive en N·m/rad et `damping`
un amortissement fini positif ou nul en N·m·s/rad. Un ressort fini sous gravité
peut conserver un écart avec la cible. Donner une nouvelle pose quand la cible
change suffit ; aucun renouvellement à chaque image n'est nécessaire.

`stop_motors()` retire les deux moteurs de toutes les articulations. Il conserve
poses et vitesses et laisse gravité, limites, friction et collisions agir. Il ne
restaure pas une configuration de moteurs antérieure à la commande de pose.
Le [test public](../../Tests/Consumer/Tests/RagdollMotors3D.sx) exerce ces appels,
les instances indépendantes, les repères modifiés et la saturation aux limites.

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
Une chaîne libre de trois sphères est aussi qualifiée face à Jolt : impulsion
excentrée sur l’extrémité sans gravité, transmission au parent, bilans de
mouvement et ancrages bornés ; puis chute symétrique sur un sol sans frottement
jusqu’au repos, à 60/120 Hz en Debug/Release. La traversée transitoire du sol
est bornée séparément de la hauteur finale. Ces recettes passives n’établissent
pas encore une qualification générale des impacts ou limites actives.

Une chaîne à racine fixe et deux sphères décalées suit aussi des cibles opposées,
revient au neutre puis redevient passive sous gravité, à 60/120 Hz en
Debug/Release. Les conventions géométriques, couples bornés et poses stabilisées
sont comparés à `Ragdoll.DriveToPoseUsingMotors` de Jolt. Cette recette sans
contact ne qualifie pas toutes les trajectoires ni les impacts motorisés.

Une [chaîne passive à butées](../../Tests/Consumer/Tests/RagdollLimits3D.sx)
transmet aussi deux impulsions angulaires opposées à travers deux articulations
de torsion bornées à −0,2/+0,35 rad, avec swing verrouillé. À 60/120 Hz et
dans deux orientations mondiales, le moment cinétique est conservé et les
butées ne créent pas d’énergie cinétique. Les ancrages, la transmission aux
parents et les angles/vitesses stabilisés sont qualifiés face au véritable
ragdoll Jolt en Debug/Release. Les observations juste avant/après impulsion
vérifient qu’elle change la vitesse sans placer les corps. Cette recette n’a
ni gravité ni contacts ; elle ne qualifie pas les impacts avec swing combiné.

Un [membre sphérique déporté à racine fixe](../../Tests/Consumer/Tests/RagdollContact3D.sx)
compose ensuite des cibles de swing/twist hors limites avec un sol sans friction.
Le membre appuie sur le sol, se soulève, revient puis redevient passif avec une
impulsion angulaire. Le témoin sans sol sépare butées et contact, à 60/120 Hz,
dans deux orientations horizontales et les deux signes latéraux. La géométrie,
les couples, la pénétration et les bilans linéaires sont contrôlés à chaque pas.
Dans les fenêtres de contact, le bilan angulaire projeté sur l’axe
d’inclinaison du levier contrôle aussi la force verticale indépendamment.
Les poses établies et les vitesses/forces moyennes sur des fenêtres de
demi-seconde sont comparées au ragdoll Jolt en Debug/Release. La tolérance
de pénétration de Jolt est explicitement réglée à 1e−6 m ; sa force normale
est inférée du bilan linéaire, tandis que Silex expose l’impulsion mesurée.
Les butées simultanées produisent chez Jolt des variations de vitesse/effort
à chaque pas : leur égalité instantanée n’est pas qualifiée. Les équilibres
moyennés ne prouvent ni les trajectoires d’impact ni les chaînes motorisées
générales à plusieurs membres libres.
