# Poser un châssis sur des suspensions de roue

`WheeledVehicle3D` associe un châssis dynamique et des roues à suspension.
Le monde cherche leurs appuis par rayon, résout ressorts et butées et applique
les réactions aux deux corps. L’application appelle seulement `world.step`.
Sans pneu optionnel, les roues appliquent seulement la suspension. Les
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
| `radius` | Rayon en mètres, `0.3` |
| `minimum_length`, `maximum_length` | Longueurs de suspension en mètres, `0.2` et `0.6` ; elles excluent le rayon |
| `stiffness` | Raideur par roue en N/m, `10000` |
| `damping` | Amortissement par roue en N·s/m, `1000` |
| `maximum_slope_angle` | Angle maximal entre normale du support et direction opposée à la suspension, `pi/3` rad |

Le ressort a pour longueur naturelle `maximum_length` ; il pousse lorsqu’il
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
