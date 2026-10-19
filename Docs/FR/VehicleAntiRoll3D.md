# Réduire le roulis avec des barres entre les suspensions

Une barre anti-roulis couple deux roues du même véhicule et s’oppose à la
différence de longueurs de leurs suspensions lorsque les deux ont un appui.
Avec des réglages de roue identiques, elle augmente la réaction du côté le plus
comprimé et réduit celle de l’autre côté. Elle conserve le mouvement vertical commun des
suspensions et leurs efforts unilatéraux : les roues ne tirent pas le sol.

L’[exemple sans rendu](../../Examples/VehicleAntiRoll.sx) compare le même
châssis sous un couple de 40 N·m, sans barre puis avec deux barres :

```sh
silex run Packages/GFX.Physics/Examples/VehicleAntiRoll.sx --release
```

Après deux secondes de charge à 120 Hz, l’exemple affiche environ 2,6° sans
barre et 0,44° avec barres.
Pour ajouter les barres lors de la création du véhicule, fournir ce fragment
avec les réglages de châssis et roues déjà construits :

```sx
Physics.WheeledVehicle3DSettings(chassis, wheels, anti_roll_bars:[
    Physics.VehicleAntiRollBar3DSettings(0,2,stiffness:1000.0),
    Physics.VehicleAntiRollBar3DSettings(1,3,stiffness:1000.0)
])
```

Ici, les roues sont rangées gauche arrière, gauche avant, droite arrière,
droite avant. Les indices désignent le tableau des roues, indépendamment des
roues motrices et des différentiels. Aucun appel de mise à jour supplémentaire
n’est nécessaire : le monde traite les barres dans `world.step`.

## Régler et lire les paires

`VehicleAntiRollBar3DSettings(left_wheel,right_wheel,stiffness:1000.0)` conserve
les deux indices et la raideur en N/m. Une raideur nulle désactive la barre ;
l’absence de barres garde le comportement précédent. Les indices doivent
être distincts, positifs ou nuls et présents dans le véhicule ; les paires
sont disjointes. Raideur et produit raideur/course doivent être finis.
Les réglages copient le tableau à la création. `anti_roll_bar_count()` et
`anti_roll_bar(i)` les lisent depuis `WheeledVehicle3DSettings` ; un indice
hors limites produit un diagnostic.

Le transfert participe au biais implicite des deux ressorts, comme dans la
référence Jolt épinglée. Sa réponse dépend aussi de l’amortissement, du pas et
des directions de contact : la raideur seule ne définit pas un ressort de
torsion indépendant de la suspension. Comparer les réglages au pas fixe choisi.
Un appui manquant annule le couplage de cette paire pour ce pas ; les observations
ordinaires `vehicle.wheel(i)` rendent les forces et contacts effectivement
résolus. Les supports dynamiques reçoivent les réactions opposées aux mêmes
points physiques. Un pas nul garde les observations précédentes.

## Preuves et portée

Le [consommateur public](../../Tests/Consumer/Tests/VehicleAntiRoll3D.sx) vérifie
copie, indépendance, barre nulle, poids, mouvement vertical, roulis sous charges
opposées, appui manquant, désactivation et conservation des moments sur support
dynamique. Le témoin `VehicleAntiRollRun.py` confronte cinq recettes avec et
sans barres, y compris raideur nulle, à 60/120 Hz en Native Debug/Release sur
macOS ARM64. Il contrôle bilans par pas, loi du ressort, symétrie, réduction
du roulis, trajectoires Jolt et forces moyennes sur fenêtres fixes ; ses gardes
refusent les sorties absentes, dupliquées, non finies ou corrompues.

Ces barres ne limitent pas explicitement un angle maximal et ne remplacent
pas un contrôle d’équilibre de moto. La comparaison de conduite avec pneus
reste distincte du témoin sans adhérence. Voir les [suspensions](VehicleSuspension3D.md),
les [pneus](PassiveTires3D.md) et les [commandes](VehicleControls3D.md).
