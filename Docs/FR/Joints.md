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

Les réglages utilisent ancres, axes et cibles en espace monde, convertis en
données locales à la création. Les familles couvrent distances et ressorts,
suppression de collision, offsets moteurs, cible souris, glissière, charnière,
soudure et suspension de roue.

La collision connectée est désactivée par défaut. Les réactions décrivent le
dernier `step` terminé et valent zéro auparavant. Modifier cibles ou vitesses
réveille les corps concernés.

Détruire un joint, ou l’un de ses corps, invalide toutes les copies du handle.
Les joints partagent le graphe Soft Step déterministe à douze couleurs avec les
contacts et participent aux îlots de sommeil.
