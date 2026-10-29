# GFX.Physics

`GFX.Physics` est une extension officielle optionnelle de GFX. Son monde 2D
est utilisable sans fenêtre, renderer, scène ni ECS. Le cœur de simulation est
écrit en Silex natif ; Box2D 3.1.1 sert uniquement d’oracle différentiel.

```text
silex install GFX.Physics
```

Le [contrôleur de personnage 3D](Character3D.md) déplace une capsule avec pentes, marches et glissement.

La [charnière 3D](Hinge3D.md) relie deux corps autour d’un axe avec des butées rigides et un moteur à vitesse cible et couple borné.

La [liaison fixe 3D](Fixed3D.md) conserve les six degrés de la pose relative de deux corps, avec capture de l’assemblage courant, repères locaux modifiables et réactions de force/couple.

La [glissière 3D](Slider3D.md) guide un chariot sur un rail tournant, avec course signée et butées rigides modifiables.

Le [moteur de glissière](SliderMotor3D.md) pilote une vitesse relative avec force maximale, freinage et mutation.

Le [frein de glissière](SliderFriction3D.md) ralentit la course sans moteur avec une force maximale mutable.

Les [bornes de force signées](SliderForceBounds3D.md) règlent des efforts différents selon le sens, en vitesse et en position.

[Butées souples de glissière](SliderSoftLimits3D.md) : compression sous charge, ressort amorti, bornes égales et mutation.

Le [servo de glissière](SliderPosition3D.md) vise une course par ressort amorti physique et force bornée.

Le [servo de charnière](HingePosition3D.md) vise un angle avec raideur, amortissement et couple borné.

Le [frein de charnière](HingeFriction3D.md) ralentit un axe sans moteur avec un couple borné, réglable à l’exécution.

Les [bornes de couple signées](HingeTorqueBounds3D.md) permettent un effort différent dans chaque sens, en vitesse ou en position.

Les [butées souples](HingeSoftLimits3D.md) amortissent les dépassements angulaires avec une raideur physique mutable.
La [commande combinée](HingeCombined3D.md) suit un angle et une vitesse actualisés ensemble.

## Corps et monde

```silex
use GFX.Physics
use STD.Math

var world = Physics.World2D()
var body = world.create_rigid_body(Physics.RigidBody2DSettings()
    ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.25))
    ..position = Math.Vec2(0.0, 10.0)
    ..rotation = 0.15
    ..friction = 0.75
)

world.step(1.0 / 60.0)
print(body.position())

world.destroy_rigid_body(body)
assert(!body.is_valid())
```

Les handles de corps, colliders et joints sont typés et générationnels. Leur
destruction invalide toutes les copies conservées. Le monde possède l’horloge,
les ressources de simulation et la frontière de mutation.
Les huit familles de joints conservent des réglages runtime typés et peuvent
être énumérées par monde ou corps via la somme `Joint2D`.

## Géométrie et contacts

La [géométrie convexe 3D autonome](Geometry3D.md) expose sphère, boîte orientée,
capsule, pose rigide et requêtes de distance, recouvrement et rayon. Le
[monde 3D](World3D.md) fait avancer les corps, résout les premiers contacts
multi-points et endort les petits îlots au repos.

Les formes comprennent boîtes, cercles, capsules, polygones convexes, segments
et chaînes. Les requêtes de distance, recouvrement, manifold, rayon et shape
cast sont pures et indépendantes d’un monde.

```silex
let capsule = Physics.ShapePlacement2D(
    Physics.Shape2D.capsule(Physics.Capsule2D(
        Math.Vec2(0.0, -0.5),
        Math.Vec2(0.0, 0.5),
        0.25
    ))
)
let wall = Physics.ShapePlacement2D(
    Physics.Shape2D.box(Physics.Box2D(Math.Vec2(1.0, 4.0), 0.1)),
    Physics.Transform2D(position:Math.Vec2(2.0, 0.0))
)
let hit = Physics.Geometry2D.shape_cast(
    capsule,
    Math.Vec2(4.0, 0.0),
    wall
)
```

Les contacts persistants sont des snapshots stables lus après `step` :

```silex
var contacts:Physics.Contact2D[] = []
world.step(1.0 / 60.0)
world.write_contacts(contacts)
print(world.contact_count())
```

La réponse dynamique Soft Step couvre toutes les formes publiques. Les
politiques de contact optionnelles sont évaluées avant le dispatch du solveur,
sur le thread qui possède `step`.

## Catalogues et parallélisme

Le package contribue ses types aux catalogues ouverts de GFX :

```silex
use GFX.Components
use GFX.Resources

let world = Resources.World2D()
let body:Components.RigidBody2D = world.create_rigid_body()
```

Un monde peut créer un executor persistant :

```silex
world.enable_parallelism(4)
```

Le nombre de workers ne change ni les paires, ni le solver, ni l’ordre logique.
Les seuils ne modifient que la répartition du même travail.

## Guides

- [Architecture](Architecture.md)
- [Monde propriétaire et durée de vie](WorldOwnership.md)
- [Intégration Application, ECS et Scene2D](ApplicationIntegration.md)
- [Intégration Application, ECS et Scene3D](Application3D.md)
- [Masse, forces et contrôle des corps](BodyControl.md)
- [Colliders et matériaux](Colliders.md)
- [Contrat de complétude Box2D](Completeness.md)
- [Debug draw physique](DebugDraw.md)
- [Contacts persistants](Contacts.md)
- [Filtrage avancé et pré-solve](ContactPolicies.md)
- [Événements, capteurs et CCD](EventsAndCCD.md)
- [Explosions et impulsions radiales](Explosions.md)
- [Requêtes géométriques](Geometry.md)
- [Requêtes spatiales du monde](WorldQueries.md)
- [Îlots actifs et sommeil](Islands.md)
- [Joints, moteurs et ressorts](Joints.md)
- [Mouvement cinématique de personnage](CharacterMover.md)
- [Réglages et compteurs du monde](WorldSettings.md)
- [Utiliser des pixels ou des centimètres](Units.md)
- [Retrouver un objet du jeu](ApplicationIdentity.md)
- [Migration de 0.4 vers 0.5](Migration.md)
- [Corpus oracle et budgets](OracleAndBudgets.md)
- [Contrat de performance](Performance.md)

L’exemple visuel central se lance depuis la racine :

```text
silex run Silex-Examples/Sources/Physics2D/RotatingPhysicsContainer/Main.sx --release
```

## Cartes tuilées

[Collisions de cartes tuilées](TileMap2D.md)

[Suivi de cible mobile par position et vitesse](SliderCombined3D.md).

[Articulation cône 3D](Cone3D.md).

[Inclinaison et torsion 3D](SwingTwist3D.md).

[Attache à six degrés de liberté](SixDOF3D.md).

[Engrenage 3D](Gear3D.md) : rapport signé, phase suivie et couples sur les deux corps.

[Crémaillère 3D](RackAndPinion3D.md) : rapport rotation/course signé, phase, couple et force.

[Poulie 3D](Pulley3D.md) : points fixes, longueur pondérée, mou et réactions aux ancrages.

Le [guidage sur chemin 3D](Path3D.md) suit une courbe Hermite en mètres avec moteurs, friction et transport d’orientation.

Un [rail sur charnière avec chariot mobile](HingedRail3D.md) transmet la charge radiale au support dynamique, avec rotation libre ou moteur borné.

[Retenir un rail chargé et libérer un contact](LoadedRail3D.md) : reprise du poids, effort moteur borné et inversion devant une paroi.

[Porter une charge avec deux charnières perpendiculaires](SpatialHinges3D.md) : poids, couples hors du plan et inversion sous charge.

[Mettre une chaîne spatiale en contact avec un plan](SpatialContacts3D.md) : contact, moment d’impulsion et libération.

[Composer une épaule et un coude motorisés](ArticulatedPose3D.md) : quatre servos, charge transmise et repères mobiles.

[Créer un assemblage ragdoll et manipuler sa pose](Ragdoll3D.md) : hiérarchie, décalages de corps, instances indépendantes, filtrage parent/enfant et suivi motorisé.

[Poser un châssis sur quatre suspensions](VehicleSuspension3D.md) : appuis par rayon ou sphère balayée, ressorts, butées, saut et réactions aux supports.

[Faire rouler les pneus et résister à la dérive](PassiveTires3D.md) : inertie, rotation, courbes de friction et réactions sur les supports.

[Braquer et freiner un véhicule](VehicleControls3D.md) : commandes persistantes, limites de braquage et freins normaux/à main.

[Motoriser les roues](VehiclePowertrain3D.md) : moteur, embrayage, transmission automatique/manuelle et différentiels.

[Réduire le roulis avec les barres entre suspensions](VehicleAntiRoll3D.md).

[Borner l’inclinaison totale du châssis](VehicleTiltLimit3D.md).

[Véhicule à deux chenilles : conduite, pivot et freinage](TrackedVehicle3D.md).

[Équilibrer et diriger une moto](Motorcycle3D.md).

- [Personnage physique 3D](PhysicalCharacter3D.md)

- [Personnage virtuel enregistré](VirtualCharacter3D.md)

- [Choix des modes et qualification des personnages](CharacterQualification3D.md)

- [Modifier un terrain par hauteurs](HeightField3D.md)

- [Terrains et assemblages de contraintes qualifiés](TerrainConstraintQualification3D.md)
