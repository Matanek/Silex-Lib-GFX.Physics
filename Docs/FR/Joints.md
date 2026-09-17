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
suppression. Les réactions décrivent le dernier `step` terminé et valent zéro auparavant.
Les mesures géométriques lisent les corps dans leur état présent, y compris
avant le premier pas et après une téléportation ou une mutation des repères.

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

## Souplesse commune et ressorts

Distance, prismatic, revolute, weld et wheel exposent `constraint_hertz`
(60 Hz par défaut), `constraint_damping_ratio` (2 par défaut) et
`set_constraint_tuning(hertz, damping_ratio)`. Le réglage commun est indépendant
des ressorts et moteurs. Sa fréquence effective est plafonnée à un quart de
l’inverse de la durée d’un sous-pas ; les accesseurs conservent la valeur
configurée. Une fréquence nulle supprime la correction de position, tandis
que la passe de relaxation conserve la contrainte de vitesse.

| Joint | Contraintes utilisant le réglage commun |
|---|---|
| Distance | Longueur rigide ; limites de longueur quand le ressort est activé |
| Prismatic | Maintien perpendiculaire à l’axe et de l’angle relatif ; limites de translation |
| Revolute | Coincidence des ancres ; limites angulaires |
| Weld | Maintien linéaire si `linear_hertz` vaut zéro et angulaire si `angular_hertz` vaut zéro |
| Wheel | Maintien perpendiculaire à l’axe ; limites de translation |

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
création comme à la mutation. La mutation réveille les corps, conserve les
impulsions accumulées et ne modifie ni ressort, ni limites, ni moteur. Un
handle détruit ou une mutation pendant `step` provoque un échec explicite.

Les ressorts conservent leur fréquence et leur amortissement propres. Ils
agissent aussi pendant la relaxation, sans le plafond du réglage commun.
Leurs impulsions sont indépendantes de celles des limites et du moteur.
Pour la distance, le ressort doit être activé pour combiner plage de longueur
et moteur. Sans ressort, ou avec des limites activées de longueurs égales, le
joint maintient `length` : le moteur et la plage ne remplacent pas cette
longueur rigide. Pour weld, une fréquence familiale positive remplace le
réglage commun uniquement sur la composante linéaire ou angulaire concernée.

## Réactions et preuves différentielles

Les forces et couples annoncés utilisent la durée d’un sous-pas. Ils suivent
les conventions de la référence Box2D 3.1.1 : la force de prismatic et le couple
de revolute excluent leur impulsion de ressort ; les réactions de distance,
wheel et weld l’incluent. La force de wheel est projetée sur l’axe conservé au
début du dernier pas, même si le corps a tourné pendant ce pas.

Les [tests de distance](../../Tests/Consumer/Tests/DistanceConstraintTuning.sx)
et les [tests des quatre autres familles](../../Tests/Consumer/Tests/JointConstraintTuning.sx)
vérifient création, lecture, mutation, indépendance des réglages et réveil.
Les témoins [réglages](../../Benchmarks/JointConstraintTuningOracle2D.sx) et
[combinaisons](../../Benchmarks/JointCombinationsOracle2D.sx) comparent
respectivement 2 688 et 3 840 observations à la référence : 1/2/4/8 sous-pas,
ancres centrales ou décentrées, corps fixe ou deux corps mobiles et axe
oblique. Ils contrôlent positions, angles, vitesses, forces et couples avec
des seuils fixes ; ils ne constituent pas une garantie universelle pour toute
scène physique.

## Cibles motor et mouse

Le joint motor corrige d’abord l’écart angulaire, puis l’écart de translation
avec une masse couplée. `linear_offset` désigne le déplacement cible entre
les corps dans le repère monde ; `angular_offset` est en radians. Le facteur
de correction, entre zéro et un, s’applique à la durée d’un sous-pas. La norme
de la force et la valeur absolue du couple restent plafonnées indépendamment.

Le joint mouse attire son ancre locale vers une cible monde. Fréquence et
amortissement règlent cette attraction ; un amortissement angulaire doux
indépendant réduit la rotation, même si `maximum_force` vaut zéro. Le couple
annoncé reflète cet amortissement. Une fréquence linéaire nulle supprime la
correction linéaire du ressort ; elle ne supprime pas l’amortissement angulaire.

Modifier cible, offset, maxima ou ressort conserve les impulsions accumulées
et réveille les corps concernés. Les nouvelles valeurs sont prises en compte
à la préparation du pas suivant. Les mutations pendant `step`, les handles
détruits et les réglages non finis ou hors domaine sont rejetés explicitement.

Le [témoin motor/mouse](../../Benchmarks/MotorMouseOracle2D.sx) compare
1 536 observations par mode : 1/2/4/8 sous-pas, ancres décentrées, centre de
masse décalé, deux corps mobiles pour motor, forces saturées ou nulles,
mutation de cible, rotation fixée et warm start désactivé. Il mesure les
deux corps et les réactions. Les [tests consommateurs](../../Tests/Consumer/Tests/MotorMouse.sx)
vérifient aussi le réveil et l’invalidation.

## Mesures instantanées et séparation des contraintes

`DistanceJoint2D.current_length()` mesure la distance actuelle entre les ancres.
`translation()` et `speed()` de prismatic et wheel mesurent le déplacement
et sa dérivée sur l’axe actuel du premier corps. Cette vitesse inclut les
vitesses angulaires et la rotation de l’axe lui-même. `RevoluteJoint2D.angle()`
donne l’angle relatif actuel, après soustraction de la référence et repli
dans l’intervalle de −π à π. Un pas artificiel n’est pas nécessaire pour
actualiser ces lectures.

Les huit familles proposent trois observations complémentaires :

- `separation()` donne le vecteur monde de la première ancre vers la seconde ;
  pour mouse, il va de l’ancre du corps vers la cible.
- `linear_separation()` donne l’écart scalaire à la contrainte rigide en mètres.
- `angular_separation()` donne l’écart angulaire à la contrainte en radians.

| Famille | Écart linéaire | Écart angulaire |
|---|---|---|
| Distance | Écart absolu à `length` sans ressort ; avec ressort, dépassement des limites actives, sinon zéro | Zéro |
| Prismatic | Norme combinant écart perpendiculaire et dépassement des limites actives | Angle relatif moins référence, replié |
| Revolute | Distance entre ancres | Dépassement des limites actives, sinon zéro |
| Weld | Distance entre ancres si `linear_hertz` vaut zéro, sinon zéro | Angle relatif moins référence si `angular_hertz` vaut zéro, sinon zéro |
| Wheel | Même mesure linéaire que prismatic | Zéro |
| Motor, mouse, filter | Zéro | Zéro |

Modifier une pose actualise ces observations sans réécrire les forces ou
couples du dernier pas. Toute lecture de ces mesures sur un joint détruit, y compris une
mesure habituellement nulle, échoue avec le diagnostic de handle périmé.

Le [témoin des observations](../../Benchmarks/JointObservationsOracle2D.sx)
compare 512 lignes en Debug et Release : huit familles, corps fixe ou mobile,
centres de masse décalés, ancres et axes obliques, limites et ressorts, mutations,
pas nul et positif, puis rotations autour de la coupure angulaire.
Les seuils absolus sont 1e-4 m/rad et 1e-3 m/s. Box2D 3.1.1 ne fournit pas
d’accesseurs translation/vitesse pour wheel : leur référence est calculée
avec les transformations et vitesses publiques de ses corps.
Voir aussi les [tests consommateurs](../../Tests/Consumer/Tests/JointObservations.sx)
et les [accès périmés](../../Tests/Consumer/check-joint-observations.py).
