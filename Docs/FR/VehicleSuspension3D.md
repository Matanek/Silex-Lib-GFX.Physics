# Poser un châssis sur des suspensions de roue

`WheeledVehicle3D` associe un châssis dynamique et des roues à suspension.
Le monde cherche leurs appuis par rayon, sphère ou cylindre balayé, résout ressorts et butées et applique
les réactions aux deux corps. L’application appelle seulement `world.step`.
Sans pneu optionnel, les appuis de suspension ne transmettent pas d’effort tangentiel. Les
[pneus passifs](PassiveTires3D.md) ajoutent roulement et adhérence ; les [commandes](VehicleControls3D.md)
ajoutent braquage et freinage. Le [groupe moteur](VehiclePowertrain3D.md) ajoute la propulsion.

L’[exemple complet sans rendu](../../Examples/VehicleSuspension.sx) pose
100 kg sur quatre suspensions. Depuis la racine du workspace :

```sh
silex run Packages/GFX.Physics/Examples/VehicleSuspension.sx --release
```

Il affiche une hauteur proche de 0,8755 m. Chaque ressort supporte environ
245,25 N ; leur somme équilibre les 981 N de poids.

## Définir les roues et le châssis

`WheeledVehicle3DSettings(chassis, wheels)` attend les réglages d’un corps
**dynamique** et au moins une `Wheel3DSettings`. Le tableau des roues est copié.
Le châssis conserve les réglages ordinaires de forme, masse, centre de masse,
inertie, collisions et sommeil. Les roues ne créent pas de corps rigides
supplémentaires et n’ajoutent pas de masse au châssis.

| Réglage de roue | Sens et valeur par défaut |
|---|---|
| `position` | Ancrage en mètres, relatif à l’origine de la forme du châssis |
| `direction` | Direction locale unitaire de détente, `(0,-1,0)` |
| `radius` | Rayon de roue en mètres, `0.3` |
| `contact` | `WheelContact3D.ray` par défaut ; `WheelContact3D.sphere(rayon)` ou `WheelContact3D.cylinder(largeur)` pour un contact volumique |
| `side_collision_width` | Largeur totale des flancs solides en mètres ; `null` désactive cette enveloppe latérale quel que soit le balayage |
| `minimum_length`, `maximum_length` | Longueurs de suspension en mètres, `0.2` et `0.6` ; elles excluent le rayon |
| `stiffness` | Raideur par roue en N/m, `10000` |
| `damping` | Amortissement par roue en N·s/m, `1000` |
| `preload_length` | Précharge en mètres, `0` ; course inchangée |
| `spring` | Fréquence/ratio ou coefficients normalisés à la masse ; `null` conserve les coefficients SI |
| `force_point` | Point local optionnel des forces ; `null` utilise le contact réel |
| `maximum_slope_angle` | Angle maximal entre normale du support et direction opposée à la suspension, `pi/3` rad |

Le ressort a pour longueur naturelle `maximum_length + preload_length` ; il pousse lorsqu’il
est comprimé et ne tire pas le support. `minimum_length` est une butée rigide
de compression. Donner deux longueurs égales supprime la course du ressort et
conserve cette butée. Les paramètres doivent être finis : rayon et raideur
positifs, amortissement et longueurs positifs ou nuls, maximum strictement
positif et supérieur ou égal au minimum. L’angle appartient à `[0,pi/2)`.

Le rayon de recherche part de l’ancrage et parcourt `maximum_length + radius`.
La longueur observée vaut la distance à l’appui moins le rayon, bornée à zéro.
Le châssis est ignoré ; les capteurs et paires interdites par les filtres de
collision sont écartés. La première surface dont la normale respecte l’angle
maximal devient le support. Les corps fixes, cinématiques et dynamiques peuvent
porter la suspension ; un support dynamique reçoit la réaction opposée au même
point de contact. La recherche par rayon ne reproduit pas la largeur d’un pneu
sur un bord étroit.

## Régler la précharge et la réponse du ressort

`preload_length` ajoute une précharge en mètres, nulle par défaut. La longueur
naturelle devient `maximum_length + preload_length` ; la course de recherche
et les deux butées restent inchangées. Une précharge de 1 cm relève ainsi
l’équilibre de 1 cm tant que les roues gardent leur appui sans atteindre une butée.

Le paramètre optionnel `spring` permet de régler la réponse sans choisir des
coefficients physiques dépendant de la masse. Fragment de création de roue :

```sx
Physics.Wheel3DSettings(Math.Vec3(), preload_length:0.01,
    spring:Physics.SuspensionSpring3D.frequency(3.0,0.8))
```

- `frequency(hertz, ratio)` choisit une fréquence strictement positive et un
  amortissement relatif positif ou nul ; `1` correspond à l’amortissement critique.
- `mass_normalized(stiffness, damping)` choisit des coefficients en s⁻² et s⁻¹.
  Le premier est strictement positif, le second positif ou nul.

Le calcul tient compte de la masse et de l’inertie du châssis, du bras autour
de son centre de masse et du haut local du véhicule. La masse du support
n’entre pas dans cette conversion. À géométrie et distribution d’inertie
identiques, doubler la masse conserve la fréquence et l’enfoncement statique.
Sans `spring`, `stiffness` et `damping` conservent leurs unités SI et leur
comportement. Une combinaison du mode alternatif avec des coefficients SI
non standards est refusée ; laisser ces deux arguments à leurs défauts.
Les valeurs et leurs conversions doivent rester finies et représentables.

`force_point:Math.Vec3(...)` choisit le point local du châssis où appliquer les
forces de suspension et de pneu. Sans ce réglage, elles agissent au contact
réel. Un point proche du centre de masse réduit le moment de roulis dû à la
force ; un point exactement au centre supprime ce moment. La réaction opposée
sur un support dynamique agit au même point mondial et conserve le bilan de
la paire. Les snapshots `contact_point` et `contact_normal` décrivent toujours
la collision réelle. Choisir ce point est un réglage de comportement du
véhicule, pas une modification de sa géométrie.

Ces réglages appartiennent aussi à `TrackedWheel3DSettings` ; les deux roues
de `Motorcycle3D` utilisent directement `Wheel3DSettings`. Le
[consommateur des réglages](../../Tests/Consumer/Tests/VehicleSuspensionSettings3D.sx)
contrôle leur héritage, les équilibres, la réponse angulaire et la conservation
des moments sur un support dynamique. Le témoin `VehicleSuspensionSettingsRun.py`
compare neuf recettes de 6 s à 60/120 Hz, avec centre de masse à l’origine,
avec Jolt original, Native Debug/Release
sur macOS ARM64 : précharge, masse doublée, modes de ressort, roulis, saut et
surcharge. Cette preuve ne qualifie pas tous les réglages possibles.

## Atteindre une arête avec une sphère

L’[exemple rayon/sphère](../../Examples/VehicleSphereContact.sx) place un ancrage
à 20 cm au-delà d’une arête. Le rayon central manque le support ; une sphère
balayée de 30 cm le trouve. Depuis la racine du workspace :

```sh
silex run Packages/GFX.Physics/Examples/VehicleSphereContact.sx --release
```

Le programme affiche `support=false` pour le rayon et `support=true` pour la
sphère, avec environ `0.5263932` m de suspension. Le choix se fait dans le
réglage de chaque roue. Fragment à utiliser lors de sa création :

```sx
Physics.Wheel3DSettings(Math.Vec3(), contact:Physics.WheelContact3D.sphere(0.3))
```

Le rayon de recherche sphérique reste distinct de `radius`, qui sert au
roulement, aux freins et au moteur. La sphère part de l’ancrage et parcourt
`maximum_length + radius - rayon_sphère`. La longueur observée vaut la
fraction touchée multipliée par ce parcours, plus `rayon_sphère - radius`,
bornée à zéro. Le rayon sphérique doit être strictement positif et inférieur
à `maximum_length + radius` ; les échelles non représentables sont refusées.

Point et normale décrivent la surface du support. Filtres, capteurs et pente
maximale sont traités avant la sélection, y compris entre feuilles d’un
composé ou d’un maillage. Le premier appui admissible est retenu ; si la sphère
chevauche déjà plusieurs surfaces, la pénétration la plus profonde est retenue.
Le monde applique les mêmes ressorts, réactions, pneus et commandes ensuite.
Une sphère approxime le volume de contact ; elle ne reproduit pas la largeur
ni la forme cylindrique d’un pneu.

## Faire compter la largeur du pneu

L’[exemple de largeur](../../Examples/VehicleCylinderContact.sx) compare deux
roues dont l’ancrage dépasse une arête de 15 cm. Une largeur de 10 cm manque
le support ; une largeur de 40 cm prend appui, avec 0,45 m de suspension :

```sh
silex run Packages/GFX.Physics/Examples/VehicleCylinderContact.sx --release
```

À la création, choisir `contact:Physics.WheelContact3D.cylinder(0.4)` pour une
largeur totale de 40 cm. Le cylindre utilise `Wheel3DSettings.radius` et part
de l’ancrage, puis parcourt `maximum_length` dans la direction de suspension.
La longueur observée est la fraction touchée multipliée par ce parcours.
Son axe suit le châssis, le braquage courant et les directions `forward`/`up`
du pneu optionnel ; sans pneu, ces directions sont `(0,0,1)` et `(0,1,0)`.
La rotation de roulement ne change pas ce volume de révolution.

Le cylindre est exact, sans arrondi des rebords. Largeur, rayon et parcours
doivent être positifs et représentables ; les échelles dont le carré devient
nul ou non fini sont refusées. Ce mode ignore `maximum_slope_angle`, comme le
détecteur cylindrique Jolt : une paroi ou un rebord peut donc porter un contact.
La normale doit néanmoins s’opposer à la direction de détente du balayage.
Un chevauchement qui s’en éloigne ne constitue pas un appui : les roues d’une
voiture sur le dos ne prennent pas le sol à travers le toit. Un plafond peut
toujours porter des roues qui pointent vers lui.
Les filtres bilatéraux, capteurs, corps désactivés et exclusion du châssis
restent appliqués. Le premier contact, ou la pénétration initiale la plus
profonde, devient le support, y compris entre feuilles d’un composé/maillage.

Pour protéger les flancs avec un balayage rayon, sphère ou cylindre, définir
`side_collision_width` dans `Wheel3DSettings` avec la largeur totale du pneu.
Par exemple, les arguments `contact:Physics.WheelContact3D.sphere(0.32)` et
`side_collision_width:0.2` associent une recherche sphérique à un pneu de 20 cm
de large. Le défaut `null` conserve les appuis de suspension seuls, y compris
pour le cylindre. La largeur doit être positive, finie et représentable
avec le rayon et la course.

Le cylindre latéral suit la longueur et le braquage courants de la roue.
Ses contacts doivent être davantage orientés selon l’axe de roue que selon
le roulement : le choc de la bande de roulement contre une marche reste du
ressort du modèle de pneu. Un contact latéral devient solide lorsque la
suspension n’a pas d’appui ou que sa compression ne peut pas dégager le flanc.
Cela empêche une roue couchée de traverser le sol par son côté lors d’un
retournement, sans bloquer le franchissement des rampes en conduite normale.
Ces contacts transmettent impulsion, frottement et réaction au châssis et au
corps touché, avec les mêmes filtres et exclusions.

Ces collisions de flanc sont discrètes ; le CCD du châssis ne balaie pas les
roues. Elles ne créent pas de corps de roue, de masse supplémentaire ni
d’événement `Contact3D` distinct. `wheel.support()`, `length` et `normal_force`
restent les observations de la suspension. Sans largeur explicite, aucun
mode de balayage ne possède cette enveloppe latérale solide. Le
[test des flancs](../../Tests/Consumer/Tests/VehicleWheelSides3D.sx) couvre le
retournement sur plan à 60/120 Hz, deux dimensions de roues, la réaction sur
une boîte dynamique et les exclusions de collision.

Une bande cylindrique peut toucher une face selon une ligne. Lorsque l’axe
est tangent au plan de contact, le monde préfère la projection du centre de
roue si ce point appartient aux deux frontières ; sinon il conserve le point
trouvé sur le support. Le ressort et les pneus réagissent toujours à ce point
physique. Différents points valides de cette ligne peuvent produire des
moments instantanés différents lors d’un choc.

Le [consommateur cylindrique](../../Tests/Consumer/Tests/VehicleCylinderContact3D.sx)
couvre largeur, braquage dès le premier pas, carrossage, filtres, pause,
chevauchements et réaction à un support dynamique. Le témoin
`VehicleCylinderContactsRun.py` compare 21 configurations et deux recettes
dynamiques à 60/120 Hz en Native Debug/Release sur macOS ARM64 : géométrie,
trajectoire, repos/poids et bilans par pas. La vitesse angulaire est comparée
par moyennes de quarts de seconde ; sa parité instantanée aux réceptions n’est
pas revendiquée. Les points de contact linéiques sont qualifiés par appartenance
aux frontières, sans égalité arbitraire de leurs coordonnées.

La normale Jolt au coin présente une erreur d’environ 0,011 par rapport à la
normale radiale analytique ; seule cette égalité est exclue, les frontières
et la longueur restant vérifiées. Silex conserve la normale analytique. La
limite du point Jolt sur plan infini tourné décrite plus bas reste distincte ;
une boîte inclinée portant ce plan valide le point physique. Ces recettes ne
qualifient ni toutes les scènes de conduite ni une parité de performance.

## Lire les appuis et provoquer une réaction

`world.create_wheeled_vehicle(settings)` crée le véhicule.
`vehicle.chassis()` donne son handle de corps rigide : appliquer une force ou
une impulsion utilise les commandes ordinaires. `wheel_count()` indique le
nombre de roues et `wheel_settings(i)` lit leurs réglages copiés.

`vehicle.wheel(i)` rend un `VehicleWheelState3D` indépendant contenant :

- `length`, longueur observée en mètres ;
- `normal_force`, effort normal résolu au dernier pas positif, en N ;
- `support()`, handle optionnel du corps d’appui ;
- `contact_point` et `contact_normal`, point et normale mondiaux de l’appui.

Longueur et contact sont évalués au début du pas ; la pose du châssis est lue
après son intégration. La force correspond à l’impulsion totale résolue pendant
ce pas, divisée par sa durée. Elle varie avec l’accélération à une butée ou lors
d’un impact. Une roue sans appui a sa longueur maximale, une force nulle et des
point/normale nuls. Un véhicule désactivé ou endormi ne résout pas de nouvel
effort. Un pas nul conserve la dernière observation.

## Possession et sommeil

`world.destroy_wheeled_vehicle(vehicle)` retire le châssis et invalide le
véhicule. Retirer directement son châssis a le même effet. Le monde contrôle
la provenance ; un handle périmé ou un indice de roue hors limites produit un
diagnostic. Les valeurs déjà lues restent des snapshots, et leurs éventuels
handles de support peuvent ensuite devenir invalides.

Les appuis participent aux îlots de sommeil et de réveil. Un support cinématique
en mouvement réveille le châssis ; détruire son support efface l’appui et le
réveille pour reprendre la chute. Plusieurs véhicules peuvent partager leurs
réglages sans partager leurs états de suspension.

## Preuves et portée

Le [consommateur public](../../Tests/Consumer/Tests/VehicleSuspension3D.sx)
contrôle poids, butée sous surcharge, saut, supports mobiles, bilans de mouvement,
centre de masse décalé, filtres, sommeil et durée de vie. Le témoin public
`VehicleSuspension` compare quatre suspensions au vrai `VehicleConstraint`
Jolt à 60/120 Hz, Native Debug/Release sur macOS ARM64, avec 12 itérations de
vitesse et 4 de position pour les deux moteurs. Le ressort est comparé par
trajectoire ; la surcharge par géométrie, bilans discrets et réactions moyennes
sur fenêtres fixées. Aucune équivalence de toutes les réactions instantanées
aux impacts ni comparaison de performance n’est annoncée.

Le [consommateur sphérique](../../Tests/Consumer/Tests/VehicleSphereContact3D.sx)
contrôle arête, portée, rejet de pente, contact initial, filtres, désactivation,
création/destruction et conservation des moments avec un support dynamique.
Le témoin `VehicleSphereContactsRun.py` confronte 19 configurations géométriques
et quatre recettes dynamiques à Jolt à 60/120 Hz en Debug/Release. La trajectoire
souple sur plan et celle des arêtes avec adhérence sont comparées ; les forces
normales et latérales réellement lues ferment les bilans de chaque moteur.
La surcharge conserve la qualification par géométrie et forces moyennes.

Sans adhérence, un équilibre symétrique sur deux arêtes est instable : un
écart initial Jolt de 1e-6 m suffit à faire basculer la caisse. La comparaison
de trajectoire de cette recette s’arrête à 1,5 s ; les bilans gardent tous les
échantillons. Enfin, le détecteur Jolt épinglé fournit un point hors surface
sur un plan infini tourné : seules longueur et normale y sont comparées. Une
boîte inclinée portant le même plan qualifie le point physique. Silex conserve
le point sur le support ; aucune égalité avec ce point Jolt incorrect n’est annoncée.

[Réduire le roulis avec les barres entre suspensions](VehicleAntiRoll3D.md).
