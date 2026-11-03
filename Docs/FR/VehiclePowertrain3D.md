# Motoriser un véhicule à roues

Un moteur et une transmission entraînent les rotors des roues motrices. Les
pneus transmettent ensuite l’effort au châssis par leur contact avec le sol.
L’[exemple complet](../../Examples/VehiclePowertrain.sx) accélère, tourne puis
s’arrête avec une boîte automatique :

```sh
silex run Packages/GFX.Physics/Examples/VehiclePowertrain.sx --release
```

## Choisir le moteur et les roues motrices

Fragment avec un châssis et une liste de roues à pneus déjà préparés :

```sx
var settings=Physics.WheeledVehicle3DSettings(chassis,wheels,
    engine:Physics.VehicleEngine3DSettings(maximum_torque:30.0),
    differentials:[Physics.VehicleDifferential3DSettings(0,2)])
var vehicle=world.create_wheeled_vehicle(settings)
vehicle.set_controls(throttle:0.5)
world.step(1.0/120.0)
```

Les indices du différentiel désignent ici les roues 0 et 2 ; leur signification
avant/arrière dépend de votre liste. Une roue motrice doit avoir un pneu et
appartenir à un seul différentiel. Un indice de −1 indique un côté absent :
`VehicleDifferential3DSettings(0)` entraîne seulement la roue 0. Toutes les
parts `engine_torque_ratio` doivent totaliser 1 ; choisir par exemple 0,5 par
pont pour une transmission intégrale. Les autres roues restent libres.

Sans `engine`, le véhicule conserve son comportement de roulement passif.
Ajouter un moteur demande au moins un différentiel. Les paramètres de moteur,
les rapports et la liste de différentiels sont copiés à la construction ;
modifier les tableaux d’origine ne reconfigure pas un véhicule existant.

## Accélérer, braquer et freiner

`set_controls(steering:0,brake:0,handbrake:0,throttle:0)` remplace la commande
complète persistante. Les paramètres omis reviennent à zéro. L’accélérateur est
fini dans [−1,1] : sa valeur absolue règle le couple moteur ; son signe choisit
le sens souhaité pour une boîte automatique. En manuel, le rapport choisi fixe
le sens. Le [braquage et les freins](VehicleControls3D.md) se combinent au moteur.

Une commande différente réveille le châssis ; répéter la même ne le réveille
pas. Le monde avance le moteur uniquement au pas positif d’un châssis actif.
Un pas nul conserve les observations ; désactiver le châssis fige aussi son
régime et ses roues. La destruction du châssis invalide les commandes et lectures.
Un accélérateur non nul, un moteur au-dessus du ralenti ou une boîte en
transition empêche le sommeil ; une commande nulle peut laisser dormir le véhicule.

## Régler le moteur

`VehicleEngine3DSettings` utilise des N·m, RPM, kg·m² et secondes :

| Paramètre | Défaut | Effet |
|---|---:|---|
| `maximum_torque` | 500 | Couple moteur maximum, positif ou nul |
| `minimum_rpm` / `maximum_rpm` | 1000 / 6000 | Ralenti imposé et régime plafonné |
| `inertia` | 0,5 | Inertie du rotor moteur, strictement positive |
| `angular_damping` | 0,2 | Amortissement du régime |
| `torque_curve` | (0;0,8), (0,66;1), (1;0,8) | Fraction de couple selon RPM/régime maximum |

La courbe interpole linéairement et conserve ses valeurs extrêmes hors de ses
points. Abscisses strictement croissantes et coefficients dans [0,1], valeurs
finies ; au moins un point. Son abscisse utilise **RPM/maximum_rpm**, y compris
au ralenti. `engine.torque(rpm,throttle:...)` évalue le couple avec un régime
fini positif ou nul et un accélérateur dans [0,1].

L’amortissement multiplie le régime par `max(0,1-angular_damping*dt)`, puis
le borne. Le moteur est ensuite couplé aux roues par l’embrayage. Les bornes de
régime sont imposées comme dans Jolt ; le ralenti peut fournir de l’énergie.
Elles ne constituent pas un modèle de calage ou de conservation globale d’énergie.

## Choisir la transmission

La boîte automatique par défaut choisit son sens depuis l’accélérateur, puis
monte et descend selon le régime. Elle n’augmente pas le rapport pendant une
perte d’appui ou un glissement longitudinal supérieur à 0,1 d’une roue motrice,
ni lorsque le régime baisse.
Pendant un changement, l’embrayage est ouvert, puis reprend progressivement.

Pour choisir les rapports vous-même, passer une configuration manuelle lors
de la création. Fragment pour un véhicule configuré en manuel :

```sx
vehicle.set_transmission(1)             // premier rapport, embrayage fermé
vehicle.set_transmission(0)             // point mort
vehicle.set_transmission(-1,clutch:0.5)  // marche arrière, embrayage partiel
```

`VehicleTransmission3DSettings(mode:VehicleTransmissionMode3D.manual)` conserve
le point mort initial jusqu’à un appel. `clutch` est fini dans [0,1] : 0 ouvre
l’embrayage, 1 le ferme. Un rapport positif indexe les rapports avant ; un rapport
négatif indexe ceux d’arrière. `gear_ratio(gear)` et les comptes de rapports
permettent d’inspecter une configuration. Les paramètres principaux sont :

| Paramètre | Défaut |
|---|---|
| `gear_ratios` | [2,66; 1,78; 1,3; 1; 0,74], tous strictement positifs |
| `reverse_gear_ratios` | [−2,9], tous strictement négatifs |
| `clutch_strength` | 10 kg·m²/s, positif ou nul |
| `switch_time` / `clutch_release_time` / `switch_latency` | 0,5 / 0,3 / 0,5 s |
| `shift_up_rpm` / `shift_down_rpm` | 4000 / 2000 RPM |

Les durées sont positives ou nulles, les seuils ordonnés et les listes non
vides. `set_transmission` exige le mode manuel. Les entrées invalides ou non
représentables provoquent un panic, comme un accélérateur sur un véhicule sans moteur.

## Répartir le couple et observer le résultat

Chaque `VehicleDifferential3DSettings` utilise un ratio positif (3,42 par défaut),
un partage `left_right_split` (0,5 : moitié de chaque côté) et une part moteur
`engine_torque_ratio` (1 par défaut). `limited_slip_ratio` vaut 1,4 ; `null`
donne un différentiel ouvert. Une limite finie supérieure à 1 redirige le couple
vers le côté le plus lent lorsque l’écart de vitesse augmente. La configuration
du véhicule offre aussi `differential_limited_slip_ratio` (1,4 par défaut, ou
`null`) pour répartir le couple entre ponts selon le même principe.

Le partage et les parts moteur sont nominaux : le glissement limité peut les
modifier. Retirer un différentiel pour déconnecter ses roues ; une part nulle
ne les déconnecte pas lorsque la redistribution limitée est active.

`vehicle.powertrain()` fournit un snapshot en lecture seule : `engine_rpm`,
`gear`, `clutch`, `switching_gear` et `engine_torque` en N·m. La boîte observée
est déjà mise à jour pour le prochain pas ; le couple appartient au pas achevé.
`vehicle.wheel(i).drive_torque` donne le couple signé transmis au rotor par le
moteur, distinct du frein et de l’amortissement. En vol, les rotors accélèrent
mais le châssis ne reçoit pas de force de propulsion. Au point mort ou avec
l’embrayage ouvert, le moteur peut monter en régime sans entraîner les roues.

Le couplage et les commandes sont qualifiés face au contrôleur Jolt réel à
60/120 Hz sur macOS ARM64 en Debug/Release. Les tests consommateurs ajoutent
solutions analytiques, réactions des corps, copies et durée de vie. Près de
l’arrêt, les états primaires et formules restent contrôlés ; les vitesses de
contact sont comparées par moyennes de phase. Aucune parité instantanée de
vitesse de contact ou d’angle mal conditionné n’est revendiquée. Les autres détecteurs de
roue, anti-roulis, chenilles et équilibre moto restent des capacités distinctes.

## Entraîner ses propres roues rigides

`WheelDrive3D` utilise ce même moteur, embrayage et boîte lorsque les jantes et
les pneus sont simulés séparément, par exemple avec des pneus souples. Le
[consommateur exécutable](../../Tests/Consumer/Smokes/WheelDrive3D.sx) vérifie
le couplage à des rotors externes. Fragment pour quatre roues déjà simulées :

```sx
var drive=Physics.WheelDrive3D(
    Physics.VehicleEngine3DSettings(maximum_torque:145.0),
    Physics.VehicleTransmission3DSettings(gear_ratios:[3.2,2.3,1.6]),
    wheel_inertias:[16.0,16.0,16.0,16.0],
    differentials:[Physics.VehicleDifferential3DSettings(0,2,engine_torque_ratio:0.5),
        Physics.VehicleDifferential3DSettings(1,3,engine_torque_ratio:0.5)],
    differential_limited_slip_ratio:1.4)
```

À chaque sous-pas, appeler `set_wheel(index,angular_velocity,grounded:...,slipping:...)`
pour chaque roue, puis `step(delta,throttle,torque_scale:1,clutch:1)`. Fournir la
vitesse angulaire **relative au châssis**, en rad/s, avec le même sens positif
pour toutes les roues. Les inerties sont les inerties effectives autour de cet
axe, en kg·m² ; elles incluent les éléments entraînés avec la jante. Les indices
et les parts de différentiel suivent les règles ci-dessus. Les tableaux sont
retenus indépendamment des modifications ultérieures du consommateur.

Appliquer ensuite `wheel_torque(index)` en N·m à la roue et sa réaction opposée
au châssis, puis avancer le monde du même `delta`. Ce contrôleur n’avance aucun
corps lui-même. Relire les vitesses réelles après contacts au pas suivant ; ne
pas appliquer une deuxième correction de vitesse ni le couple moteur brut.
Les freins restent à la charge du montage. `grounded` et `slipping` renseignent
la protection de montée de rapport, sans créer de force de contact.

Le pas est fini dans [0,1] seconde et un pas nul conserve l’état et les couples.
`torque_scale` est fini et positif ou nul ; il multiplie le couple de combustion,
par exemple pour un boost. `clutch`, fini dans [0,1], multiplie l’embrayage de la
boîte : il permet une prise progressive au démarrage ou une ouverture pendant
le freinage. Le ralenti imposé peut autrement pousser des roues immobiles.
En mode manuel, `set_transmission(gear,clutch:...)` conserve son rôle ; la
pression passée à `step` se multiplie à cette commande. Les entrées invalides
provoquent un panic.


`differential_limited_slip_ratio` règle aussi la redistribution entre vos ponts.
Le défaut `null` conserve leurs parts nominales ; une valeur finie supérieure à
1, par exemple 1.4, dirige davantage de couple vers le pont qui tourne le moins
vite lorsque les vitesses divergent. Ce réglage est indépendant du glissement
limité gauche/droite propre à chaque différentiel. Il permet d’alimenter les
roues chargées lorsqu’un autre essieu patine.

`state()` fournit `VehiclePowertrainState3D` : régime, rapport, embrayage effectif,
transition et couple moteur. Ces observations peuvent alimenter un tableau de
bord ou un moteur sonore. GFX.Physics ne dépend d’aucune bibliothèque audio.
