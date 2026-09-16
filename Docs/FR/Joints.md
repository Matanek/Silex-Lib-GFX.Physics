# Joints, moteurs et ressorts

`World2D` possède huit familles typées : distance, filter, motor, mouse,
prismatic, revolute, weld et wheel. Aucun solver row, couleur, slot ou base de
contrainte commune n’est public.

```silex
var hinge = world.create_revolute_joint(
    chassis,
    arm,
    Physics.RevoluteJoint2DSettings()
        ..anchor = Math.Vec2(0.0, 1.0)
        ..lower_angle = -0.5
        ..upper_angle = 0.5
        ..motor_speed = 2.0
        ..maximum_motor_torque = 40.0
        ..limit_enabled = true
        ..motor_enabled = true
)
```

Les réglages de création utilisent ancres, axes et cibles en espace monde,
convertis en données locales à la création. Les handles donnent ensuite accès
aux corps connectés et aux repères locaux effectivement conservés. Chaque
famille expose ses propriétés pertinentes : longueur, limites, ressort,
moteur, cible, offsets, maxima, hertz et amortissement. Leurs mutateurs valident
les valeurs, annulent les impulsions devenues incompatibles et réveillent
l’îlot concerné. Ils échouent comme toute mutation du monde pendant `step`.

```silex
hinge.set_limits(true, -0.75, 0.75)
hinge.set_spring(true, 4.0, 0.7)
hinge.set_motor(3.0, 60.0)
```

La collision connectée est désactivée par défaut et peut être modifiée à
l’exécution, sauf pour `FilterJoint2D` dont l’intention reste toujours la
suppression. Les réactions et mesures décrivent le dernier `step` terminé et
valent zéro auparavant. `separation()` calcule la séparation courante des
repères sans exposer les lignes ni les impulsions du solveur.

`world.write_joints(buffer)` énumère tous les joints dans leur ordre stable de
création. La surcharge `world.write_joints(body, buffer)` ne conserve que ceux
attachés au corps. Le tableau contient la somme étiquetée `Joint2D` ; un
`match` restitue le handle distance, filter, motor, mouse, prismatic, revolute,
weld ou wheel et donc son API spécialisée.

Détruire un joint, ou l’un de ses corps, invalide toutes les copies du handle.
Les joints partagent le graphe Soft Step déterministe à douze couleurs avec les
contacts et participent aux îlots de sommeil.

Les preuves exécutables sont
[`Joints.sx`](../../Tests/Consumer/Tests/Joints.sx) et
[`JointRuntimeConfiguration.sx`](../../Tests/Consumer/Tests/JointRuntimeConfiguration.sx).

## Souplesse de la distance rigide

Sans ressort ni limite, `DistanceJoint2D` utilise `constraint_hertz` (60 Hz
par défaut) et `constraint_damping_ratio` (2 par défaut) pour corriger l’écart
à la longueur cible. Les réglages sont indépendants de `spring_hertz` et de
`spring_damping_ratio`. La fréquence effective est plafonnée à un quart de
l’inverse de la durée d’un sous-pas ; les accesseurs conservent la valeur
configurée. Une fréquence nulle supprime la correction de position, mais la
relaxation continue de contraindre la vitesse relative.

```silex
var tether = world.create_distance_joint(chassis, arm,
    Physics.DistanceJoint2DSettings()
        ..first_anchor = Math.Vec2()
        ..second_anchor = Math.Vec2(2.0, 0.0)
        ..length = 1.0
        ..constraint_hertz = 5.0
        ..constraint_damping_ratio = 2.0)
tether.set_constraint_tuning(8.0, 3.0)
assert(tether.constraint_hertz() == 8.0)
assert(tether.constraint_damping_ratio() == 3.0)
```

Fréquence et amortissement doivent être finis et positifs ou nuls, à la
création comme à la mutation. La mutation réveille les corps et annule les
impulsions précédentes ; elle conserve ressort, limites et moteur. Ces réglages
ne s’appliquent actuellement qu’au parcours de distance rigide sans limite.
L’équivalence des combinaisons ressort/limites et celle des autres familles
restent à qualifier dans la matrice de complétude.

Les forces et couples annoncés utilisent la durée d’un sous-pas, correspondant
à l’impulsion conservée par Soft Step. Les
[tests publics](../../Tests/Consumer/Tests/DistanceConstraintTuning.sx) vérifient
l’API, le réveil et l’unité de force. Le
[témoin différentiel](../../Benchmarks/DistanceTuningOracle2D.sx) compare
224 observations transitoires à Box2D pour 1, 2, 4 et 8 sous-pas.
