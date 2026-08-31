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
