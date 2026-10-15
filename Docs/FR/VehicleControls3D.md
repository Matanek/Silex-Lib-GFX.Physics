# Braquer et freiner un véhicule

Les roues à pneus peuvent braquer et freiner leur rotation. Le contact transmet
alors les efforts au châssis et au support ; le monde garde le pas de simulation.
L’[exemple complet sans rendu](../../Examples/VehicleControls.sx) lance un
véhicule à 3 m/s, le fait tourner puis l’arrête :

```sh
silex run Packages/GFX.Physics/Examples/VehicleControls.sx --release
```

## Choisir les roues qui braquent et freinent

Fragment à intégrer à la liste de roues d’un `WheeledVehicle3DSettings` :

```sx
Physics.Wheel3DSettings(
    Math.Vec3(-0.6, 0.0, 1.0),
    tire:Physics.Tire3DSettings(),
    maximum_steering_angle:Math.radians(30.0),
    maximum_brake_torque:1500.0,
    maximum_handbrake_torque:0.0
)
```

`maximum_steering_angle` vaut 0 par défaut : cette roue ne braque pas. Une
valeur signée entre −π/2 et π/2 fixe l’amplitude ; une valeur négative permet
le contre-braquage. `steering_axis` est un axe local unitaire fini, +Y par
défaut. Le braquage tourne le repère du pneu autour de cet axe, sans déplacer
l’ancrage ni changer la direction de suspension.

Les couples maximum de frein et de frein à main sont positifs ou nuls, en N·m,
finis et représentables relativement au rayon. Leurs défauts sont respectivement
1500 et 0. Régler le frein à main seulement sur les roues souhaitées, par exemple
celles de l’arrière. Sans pneu, le braquage reste observable mais aucun effort
tangentiel ni couple de frein n’est exercé. Voir les [pneus passifs](PassiveTires3D.md).

## Donner une commande persistante

Fragment avec un véhicule déjà créé :

```sx
vehicle.set_controls(steering:0.4)
world.step(1.0/120.0)
vehicle.set_controls(brake:1.0)
world.step(1.0/120.0)
vehicle.set_controls()
```

`set_controls(steering:0, brake:0, handbrake:0, throttle:0)` remplace la commande complète.
Les paramètres omis reviennent à zéro. Direction finie dans [−1,1], freins finis
dans [0,1] ; les valeurs invalides provoquent un panic. La commande persiste
jusqu’au prochain appel et prend effet au prochain pas positif actif. Un pas
nul conserve les observations ; un châssis désactivé conserve angles et rotation.

La direction positive signifie **droite du véhicule**, selon son repère avant
et haut. Avec avant +Z et haut +Y, cette droite est −X. L’angle géométrique vaut
`-steering*maximum_steering_angle` autour de l’axe local ; le snapshot
`vehicle.wheel(i).steering_angle` le fournit en radians pour le rendu.

Une commande différente réveille le châssis ; répéter la même commande ne le
réveille pas. Direction et freins au repos n’interdisent pas son sommeil.
Le véhicule doit être vivant et la mutation doit avoir lieu hors du pas du monde.

## Observer le freinage

Les deux commandes de frein additionnent leurs couples par roue. Le frein
ralentit le rotor sans l’inverser ; s’il peut le bloquer, le couple restant tient
la roue bloquée contre le sol, dans la limite de son adhérence. Sur un support
sans friction, la roue peut être bloquée alors que le châssis continue à glisser.
En vol, le frein agit sur la rotation sans ralentir le déplacement du châssis.

Le snapshot ajoute `brake_torque`, couple effectivement exercé, signé selon
la rotation de roue et exprimé en N·m. Son amplitude reste bornée par le couple
commandé. Il inclut la réaction qui tient le rotor bloqué ; l’amortissement du
pneu reste distinct. Les forces longitudinales/latérales existantes décrivent
la réaction du contact sur le châssis, avec l’opposé sur le support.

L’angle de roue avance après amortissement, avant application du frein. Les
vitesses, forces et couples sont lus après résolution. La disparition d’un
support efface ses observations de contact ; la commande reste mémorisée pour
le prochain pas. La destruction du châssis invalide les commandes.

[Le groupe moteur et la transmission](VehiclePowertrain3D.md) permettent aussi
d’accélérer ces roues avec `throttle`.

## Preuves de comportement

Le [consommateur public](../../Tests/Consumer/Tests/VehicleControls3D.sx)
contrôle arrêt dans les deux sens, couples bornés, frein arrière, vol analytique,
contre-braquage, supports, sommeil et durée de vie. Le vrai contrôleur Jolt
sert de référence en Debug/Release à 60/120 Hz sur macOS ARM64. Trajectoires,
rotations et bilans restent contrôlés à chaque pas. Près de l’arrêt, les vitesses
de glissement sont comparées ; les ratios restent vérifiés par leur formule
mais leur égalité entre moteurs n’est pas revendiquée lorsque leur dénominateur
tend vers zéro. Le coût d’exécution n’est pas qualifié par ces parcours.
