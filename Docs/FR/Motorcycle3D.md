# Équilibrer et diriger une moto

`World3D.create_motorcycle` assemble un châssis dynamique, une roue avant et une
roue arrière avec une assistance d’équilibre. Les contacts, suspensions et pneus
restent physiques ; le monde applique les couples d’assistance pendant son pas.
Couper l’assistance laisse la moto tomber.

L’[exemple sans rendu](../../Examples/Motorcycle.sx) part d’une inclinaison de
0,2 rad, revient à la verticale sur ses deux appuis puis détruit la moto.
Depuis la racine du workspace ou du groupe de Spec :

```sh
silex run Packages/GFX.Physics/Examples/Motorcycle.sx
```

## Décrire le châssis et les deux roues

`Motorcycle3DSettings(chassis, front, rear)` réutilise `RigidBody3DSettings` et
`Wheel3DSettings`. Chaque roue exige un `Tire3DSettings`. Les positions de roue
et directions de suspension sont locales au châssis. Dans les observations,
`wheel(0)` désigne l’avant et `wheel(1)` l’arrière.

L’empattement est la distance avant/arrière projetée sur `forward`, depuis les
extrémités des suspensions détendues ; il doit être positif. `up` vaut Y et
`forward` vaut Z par défaut. Ces deux directions doivent être unitaires et
orthogonales. Les réglages conservent leurs propres valeurs de roues et de
châssis ; modifier leur source après création ne reconfigure pas une moto.

Le moteur est facultatif. Le paramètre `engine` ajoute le
[moteur et la transmission](VehiclePowertrain3D.md) partagés avec les véhicules
à roues ; `drive_ratio`, égal à 3,42 par défaut, entraîne la roue arrière.
Sans moteur, un `throttle` non nul et la lecture du groupe moteur sont refusés.
`set_controls(steering, brake, handbrake, throttle)` et `set_transmission`
gardent les conventions des [commandes de roue](VehicleControls3D.md).

## Régler l’assistance

`MotorcycleBalance3DSettings` décrit la cible et les gains de l’actuateur :

| Réglage | Sens | Défaut |
| --- | --- | --- |
| `maximum_lean_angle` | Inclinaison maximale de la cible, dans `[0, pi/2)` | `pi/4` rad |
| `stiffness` | Couple proportionnel à l’erreur, en N·m/rad | `5000` |
| `damping` | Amortissement, en N·m·s/rad | `1000` |
| `integral_gain` | Gain de l’erreur intégrée, en N·m/(rad·s) | `0` |
| `integral_decay` | Décroissance de l’intégrale hors appui | `4` s⁻¹ |
| `smoothing` | Poids de la cible précédente, dans `[0, 1]` | `0.8` |

Les gains et la décroissance sont positifs ou nuls, finis et représentables.
`smoothing=0` suit directement les efforts observés ; `smoothing=1` conserve
la direction précédente après son initialisation. Le lissage est par pas.
La décroissance multiplie l’intégrale par `max(0, 1-integral_decay*dt)` à chaque
appel du solveur sans appuis chargés : son effet dépend donc aussi des
itérations. Le défaut `integral_gain=0` n’utilise pas cette intégrale.

Fragment, sur une moto déjà créée :

```sx
bike.set_balance_settings(Physics.MotorcycleBalance3DSettings(
    stiffness:3000.0, damping:700.0, maximum_lean_angle:0.5))
bike.set_balance_enabled(false)
bike.set_balance_enabled(true)
```

Changer les réglages conserve l’intégrale ; désactiver l’assistance la remet
à zéro au prochain pas actif. Ces mutations réveillent le châssis.

## Inclinaison, direction et appuis

La cible suit la résultante des efforts normaux et latéraux du pas précédent,
projetée perpendiculairement à l’avant de la moto, puis bornée par
`maximum_lean_angle`. `lean_target()` donne cette direction monde ; il renvoie
le vecteur nul avant le premier pas positif.

L’assistance applique un couple autour de l’axe avant seulement lorsque les deux
roues ont un contact chargé. Une correction de vitesse du châssis compense la
variation moyenne de vitesse aux contacts. Il s’agit d’un actuateur externe :
aucun couple opposé n’est appliqué aux supports. Sans appui, aucune assistance
ne redresse la moto en vol.

La direction est limitée selon l’empattement, la vitesse avant au carré, la
gravité et la chasse de chaque roue. `set_steering_limit_enabled(false)` retire
cette limite sans couper l’équilibre. Les deux activations sont indépendantes
et actives par défaut. La limite porte sur l’amplitude du braquage : inverser
le signe de l’angle maximal d’une roue ou celui de son axe conserve la convention
signée des roues. `maximum_tilt_angle`, distinct de la cible d’assistance,
reste une [limite conique](VehicleTiltLimit3D.md) facultative de valeur `pi`.

Le [filtre de pente des roues](VehicleSuspension3D.md) reste relatif à leur
direction de suspension. Son défaut `pi/3` peut libérer un appui lorsque la moto
tombe. Sur le plan de comparaison, le témoin règle explicitement
`pi/2-1e-6` pour comparer les mêmes contacts au testeur Jolt à verticale monde.

## Possession et qualification

Le monde possède le châssis et la simulation. `destroy_motorcycle`, la destruction
de son châssis ou la fin de vie du monde invalident tous ses handles ;
`is_valid()` reste consultable. Un monde étranger ne peut pas détruire la moto.
Les réglages sont validés avant insertion. `step(0)` ne calcule ni pose ni
nouvelle cible ; les commandes et mutations de configuration ne sont pas permises
pendant un pas.

La comparaison actuelle couvre 16 recettes, 60/120 Hz et Native Debug/Release
sur macOS ARM64 : équilibre, désactivation/réactivation, saut, virages sur élan,
lissage, limite de cible et direction en vol. Le moteur a un couple nul dans
ces recettes. Les sorties des deux modes sont identiques. Dès que le centre
de la moto qui tombe sans assistance passe sous 0,2 m, la preuve porte sur
l’événement et un état borné, sans angle de rebond pointwise. Propulsion composée, terrains et autres
détecteurs de roue nécessitent leurs campagnes propres ; voir les
[témoins et budgets](OracleAndBudgets.md).
