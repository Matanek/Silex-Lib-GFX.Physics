# Limiter le tangage et le roulis d’un véhicule

`maximum_tilt_angle` définit l’inclinaison totale autorisée entre le haut du
châssis et la verticale opposée à la gravité. Cette aide de stabilité forme
un cône : le même angle borne les combinaisons de tangage et de roulis,
tandis que le lacet reste libre. Le défaut `Math.pi()` laisse le véhicule libre.

L’[exemple sans rendu](../../Examples/VehicleTiltLimit.sx) part de 60° en vol
et compare le véhicule libre avec un cône de 30° :

```sh
silex run Packages/GFX.Physics/Examples/VehicleTiltLimit.sx --release
```

Après une seconde à 120 Hz, il affiche environ 60° puis 30°. Pour configurer
un véhicule dont les réglages de châssis et les roues sont déjà construits :

```sx
Physics.WheeledVehicle3DSettings(chassis, wheels,
    maximum_tilt_angle:Math.pi()/6.0,
    up:Math.Vec3.up())
```

`up` est un axe unitaire dans le repère local du châssis. La verticale mondiale
suit la gravité du monde ; une gravité nulle conserve la dernière verticale.
Avant le premier pas avec gravité non nulle, cette verticale est initialisée
avec `up`. Modifier le haut local demande de recréer le véhicule.

## Modifier la limite pendant la simulation

`vehicle.maximum_tilt_angle()` lit la limite en radians.
`vehicle.set_maximum_tilt_angle(angle)` la remplace et réveille le châssis.
La nouvelle limite est traitée au prochain pas positif ; `world.step(0.0)`
conserve la pose et les observations. Chaque instance possède sa limite.
Après destruction du véhicule, lecture et mutation produisent un diagnostic.

L’angle doit être fini dans `[0, pi]`, et `up` doit être fini et unitaire.
La lecture reconstruit l’angle depuis son cosinus et peut donc différer du
réglage initial par arrondi, surtout près de zéro. Les barres anti-roulis et les suspensions
restent configurées indépendamment.

## Comprendre la correction

La limite applique une impulsion angulaire unilatérale au châssis lorsqu’il
sort du cône, puis corrige progressivement sa pose pendant les passes de
position. Elle agit aussi sans appui. Le monde possède ce travail : l’application
continue d’appeler seulement `world.step`. La translation n’est pas corrigée
par cette aide de stabilité.

Une pose initiale hors du cône revient progressivement vers la borne. Un angle
nul est accepté mais sa récupération devient lente près de la verticale.
Le nombre de passes de position influence cette récupération ; aucune borne
instantanée d’orientation après un choc n’est promise.

Au retournement exactement opposé à la verticale, l’axe de correction est
indéterminé. Comme la référence Jolt, le véhicule réutilise son axe précédent ;
une instance neuve exactement retournée peut donc rester inversée. Créer une
pose légèrement inclinée ou fournir un mouvement initial définit une direction
physique de récupération. Cette aide ne constitue pas un contrôleur d’équilibre
pour une moto.

## Preuves et portée

Le [consommateur public](../../Tests/Consumer/Tests/VehicleTiltLimit3D.sx)
exerce axes opposés et diagonaux, vol, translation, lacet, limites mutées,
gravité tournée puis nulle, haut local distinct, zéro pas, sommeil et destruction.
`VehicleTiltLimitRun.py` confronte ces situations au vrai `VehicleConstraint`
Jolt épinglé à 60/120 Hz en Native Debug/Release sur macOS ARM64. Les bilans
libres sont vérifiés indépendamment des comparaisons entre moteurs.

Le cas avec appuis part à plat et borne le roulis à .0025 rad (environ .14°)
pour isoler la ligne angulaire sous une charge de 40 N·m avec anti-roulis,
puis un bond et une reprise des appuis. Les retours en butée après forte charge et grand
basculement libre restent hors de cette qualification bornée. Voir les
[barres anti-roulis](VehicleAntiRoll3D.md) et les [suspensions](VehicleSuspension3D.md).
