# Conduire un véhicule à deux chenilles

`TrackedVehicle3D` associe un châssis dynamique à deux bandes de roues suspendues.
Le moteur entraîne les bandes ; leurs contacts transmettent les efforts au
châssis et aux supports. Le monde possède le pas de simulation : l’application
appelle `world.step`, envoie des commandes et lit les états.

L’[exemple sans rendu](../../Examples/TrackedVehicle.sx) effectue une réception,
une accélération puis un freinage sur un plan. Depuis la racine du workspace :

```sh
silex run Packages/GFX.Physics/Examples/TrackedVehicle.sx --release
```

## Définir les roues et les deux bandes

Créer les roues avec `TrackedWheel3DSettings(position, ...)`, puis deux
`VehicleTrack3DSettings(driven_wheel, wheels, ...)`. Les indices désignent le
tableau de roues du véhicule. Chaque roue appartient à exactement une bande ;
la roue motrice doit appartenir à celle-ci. Les deux bandes sont non vides.

`TrackedVehicle3DSettings(chassis, wheels, left, right, ...)` conserve ces choix.
Le tableau de roues et les tableaux d’indices sont copiés. Le châssis doit être
dynamique et conserve ses propriétés de corps rigide. Le monde crée un seul
corps pour le véhicule ; les roues n’ajoutent pas de masse au châssis.

| Réglage de roue | Sens et défaut |
| --- | --- |
| `position` | Ancrage local, en mètres |
| `direction` | Détente unitaire locale, `(0,-1,0)` |
| `radius` | Rayon, `0.3 m` |
| `minimum_length`, `maximum_length` | Course hors rayon, `0.2` et `0.6 m` |
| `stiffness`, `damping` | Ressort `10000 N/m`, amortisseur `1000 N·s/m` |
| `contact` | Recherche par rayon ; sphère/cylindre disponibles dans le socle |
| `maximum_slope_angle` | Filtre de pente des rayons/sphères, `pi/3 rad` |
| `forward`, `up` | Axes locaux de la roue, `(0,0,1)` et `(0,1,0)` |
| `longitudinal_friction`, `lateral_friction` | Coefficients constants, `4` et `2` |

Le contact combine les coefficients de roue et de support par moyenne
géométrique. Les contrats de [suspension et de détection](VehicleSuspension3D.md)
s’appliquent. Une roue sans appui n’applique aucun effort au support.

| Réglage de bande | Sens et défaut |
| --- | --- |
| `driven_wheel` | Roue motrice dont le rayon définit la vitesse de bande |
| `wheels` | Indices distincts, incluant la roue motrice |
| `inertia` | Inertie de la bande et de ses roues vue sur la motrice, `10 kg·m²` |
| `angular_damping` | Amortissement angulaire, `0.5 s⁻¹` |
| `maximum_brake_torque` | Couple maximal du frein de bande, `15000 N·m` |
| `differential_ratio` | Rapport entre boîte et roue motrice, `6` |

Les roues d’une bande ont une vitesse linéaire commune. Leurs vitesses angulaires
peuvent différer si leurs rayons diffèrent : `omega_i = omega_motrice *
rayon_motrice / rayon_i`. L’inertie est portée par la bande entière.
Les paramètres et produits nécessaires doivent être finis et représentables ;
les topologies invalides sont refusées avant insertion du châssis dans le monde.

## Commander la conduite

Créer le véhicule avec `world.create_tracked_vehicle(settings)`.
`set_controls(throttle, left_ratio, right_ratio, brake)` remplace les commandes
persistantes ; leurs valeurs par défaut sont `0, 1, 1, 0`.

| Commande | Domaine et effet |
| --- | --- |
| `throttle` | `[-1,1]` ; amplitude des gaz, signe de direction pour la boîte automatique |
| `left_ratio`, `right_ratio` | `[-1,1]`, chacun non nul ; vitesses relatives et sens des bandes |
| `brake` | `[0,1]` ; fraction du couple de frein de chaque bande |

En ligne droite, garder les ratios à `1`. Pour tourner vers la gauche du
véhicule, choisir `left_ratio:0.5, right_ratio:1.0` ; inverser les deux pour
la droite. `left_ratio:-1.0, right_ratio:1.0` commande une contre-rotation pour
pivoter. Le résultat dépend de l’adhérence, des charges et du couple disponible.
Zéro est refusé pour ces ratios dans ce modèle couplé.

`set_controls()` relâche les gaz et les freins et remet les deux ratios à 1.
`set_controls(brake:1.0)` freine. Sans adhérence, le frein arrête les rotors
mais ne peut retenir ou arrêter le châssis au sol.

Les [réglages moteur et boîte](VehiclePowertrain3D.md) sont communs. Les défauts
chenille sont un moteur de 500N·m, ralenti 500 et maximum 4000RPM, avec rapports
avant 4/3/2/1, arrière −4/−3 et seuils 1000/3500RPM. En mode manuel, appeler
`set_transmission(gear, clutch:1.0)` ; les rapports négatifs désignent l’arrière,
0 le point mort. Le signe des ratios de bandes reste un choix distinct.

Le contrôleur utilise un couplage idéal entre les bandes. Moteur connecté,
son régime suit les bandes avec les bornes de ralenti/régime ; il ne reproduit
pas l’embrayage implicite automobile : `clutch` multiplie le couple transmis,
et `clutch_strength` n’intervient pas dans ce contrôleur. Un ralenti nul avec deux bandes arrêtées
ne démarre pas ce système couplé. L’upshift automatique exige un appui et des
bandes tournant dans le même sens. Le frein agit d’abord sur la rotation de
bande puis ses contacts transmettent le couple résiduel, limité par l’adhérence.

## Observer, suspendre et détruire

- `chassis()` donne le corps rigide ; `wheel_count()`, `wheel_settings(i)` et
  `wheel(i)` donnent géométrie, appui, longueur, angle, vitesse et efforts.
- `track(VehicleTrackSide3D.left/right)` donne vitesse angulaire motrice,
  vitesse linéaire de bande, couple moteur appliqué et couple de frein signé.
- `track_settings(side)` relit les réglages de bande ; `powertrain()` donne
  régime, rapport, embrayage et changement de rapport. Les couples moteur/frein
  de bande se lisent sur `track` ; les roues exposent leurs efforts au contact.
- `set_track_angular_velocity(side, velocity)` initialise/modifie le rotor en
  rad/s et réveille le châssis ; les observations des roues sont actualisées au
  prochain pas positif. Leurs angles intègrent la vitesse avant couple du pas.

Un pas nul conserve les observations. Désactiver le châssis fige les bandes et
le moteur ; réactiver reprend la simulation. Des commandes inchangées ne le
réveillent pas. Les gaz empêchent le sommeil ; une vitesse de roue supérieure à 10°/s
maintient aussi le châssis éveillé.
Les roues publiées après un pas reflètent la vitesse finale de leur bande,
y compris lorsqu’une roue perd son appui.

`world.destroy_tracked_vehicle(vehicle)` retire le châssis et ses suspensions.
Détruire directement `vehicle.chassis()` invalide aussi le handle ; détruire
un support retire ses références d’appui. La fin du monde invalide ses handles.
`is_valid()` permet de le vérifier ; les autres accès à un véhicule expiré
sont refusés. Chaque véhicule reste attaché à son monde d’origine.

`maximum_tilt_angle` et `up` ainsi que les barres anti-roulis utilisent le
socle commun. La campagne décrite ci-dessous n’active ni barres ni protection.

## Qualification disponible

La référence Jolt 5.6.0 épinglée est comparée en Silex Native Debug/Release sur
macOS ARM64. Seize recettes en vol couvrent ratios, inerties, rayons différents,
boîte, freinage, changement de commande et limite de régime. Six recettes au
sol utilisent une boîte manuelle et des rayons sur un plan : avant/arrière,
courbes opposées, pivot,
absence d’adhérence puis retour au repos. Les contacts sphériques/cylindriques
restent disponibles par le socle ; cette campagne chenille ne les qualifie pas.

Les comparaisons conservent les bilans par pas, poses et vitesses de châssis,
charges normales et efforts résultants, avec limites explicitées dans le
[protocole de qualification](OracleAndBudgets.md). Le partage tangentiel entre
roues d’une bande n’est pas une force individuelle unique ; sa parité n’est pas
annoncée. Ce modèle de bandes idéales ne simule pas des maillons articulés,
une géométrie de chenille continue ou tous les terrains.
