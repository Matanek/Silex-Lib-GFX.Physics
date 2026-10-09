# Porter une charge avec deux charnières perpendiculaires

Une chaîne fixe → bras → charge peut transmettre le poids à travers deux
[charnières](Hinge3D.md) dont les axes sont perpendiculaires. Le premier moteur
retient le bras autour de Z ; le second retient ou déplace la charge autour de X.
La charge déportée en Z produit aussi un couple autour de X au pivot : les
composantes bloquées de la charnière participent à ce soutien.

Le [consommateur exécutable](../../Tests/Consumer/Tests/SpatialHinges3D.sx)
vérifie le maintien, puis le déplacement, l’inversion et le freinage.
Depuis la racine du workspace :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialHinges3D.sx
```

## Disposer les corps et les repères

Le bras a une masse de 2 kg, une inertie isotrope de 0,4 kg·m² et son centre
initial en `(0.5,0,0)` m. La charge a une masse de 1 ou 2 kg, une inertie de
0,2 kg·m² et son centre en `(1,0,±0.8)` m. Toutes les poses initiales ont une
rotation identité ; les vitesses sont nulles. La gravité vaut `(0,-9.81,0)`.

La première charnière relie le pivot fixe au bras, au point monde `(0,0,0)`.
Son ancrage local sur le bras est `(-0.5,0,0)` ; l’axe Z et la normale X sont
ceux des réglages par défaut. La seconde relie le bras à la charge au point
monde `(1,0,0)` : ancrages locaux `(0.5,0,0)` sur le bras et `(0,0,∓0.8)`
sur la charge. Ses deux axes locaux sont X et ses normales locales Y.

`HingeMotor3D(0.0,60.0)` retient le bras avec une capacité de 60 N·m.
Le second moteur dispose de 40 N·m : il demande zéro, ou ±0,2 rad/s, inverse
après 2/3 s puis demande zéro après 4/3 s. Un moteur en vitesse freine mais
ne ramène pas à un angle précis ; choisir le [servo de position](HingePosition3D.md)
pour cette autre intention. Le plafond doit couvrir le poids et les accélérations.

## Interpréter les réactions

`reaction_force()` et `reaction_torque()` donnent respectivement une force et
un couple dans le repère monde, appliqués au second corps. Le premier reçoit
leurs opposés. Le couple ne comprend pas le moment de la force d’ancrage :
ajouter `lever_arm.cross(reaction_force)` pour obtenir le couple total autour
du centre de masse. Utiliser le bras de levier au moment où l’impulsion est
appliquée, avant l’intégration du pas.

Au repos, la seconde force reprend le poids de la charge, la première les
poids des deux corps. Avec les poses initiales, la première réaction de couple
est proche de `(-mass*9.81*z,0,(1+mass)*9.81)` N·m ; la seconde de
`(-mass*9.81*z,0,0)` N·m, où `z` est le déport signé de la charge.
Le moteur de la première charnière ne fournit que la composante Z ; ses axes
bloqués transmettent le couple X. `motor_torque()` est un effort scalaire
selon l’axe de la liaison, tandis que `reaction_torque()` inclut également
les composantes bloquées. Après mouvement, calculer l’équilibre avec les
positions et bras de levier courants.

Pendant le mouvement, le bilan de rotation propre inclut ces moments d’ancrage.
Le moment cinétique total comprend aussi `position.cross(mass*velocity)` pour
chaque corps. La gravité et la réaction du pivot sont les efforts externes ;
les réactions internes de la seconde charnière s’annulent dans ce bilan.

## Portée vérifiée

Deux masses, deux déports, 60/120 Hz et maintien/déplacement donnent 16 recettes
de deux secondes. Silex et Jolt épinglé sont qualifiés indépendamment en Native
Debug/Release sur macOS ARM64. Les bilans linéaires restent sous 1e−5 N·s,
ceux de rotation sous 0,001 N·m·s par pas et 0,01 N·m·s cumulés pour le moment
total. Ces bornes tiennent compte de l’intégration et des corrections de pose ;
elles ne revendiquent pas une conservation discrète exacte.

Ancrages et axes restent sous 0,005 m/rad, l’angle du bras et celui de la charge
retenue sous 0,02 rad. Le parcours mobile doit dépasser 0,08 rad et atteindre
les deux sens de vitesse au-delà de 0,15 rad/s. Les vitesses finales restent
sous 0,005 m/s ou rad/s, les erreurs de poids et de couple sous 0,05 N et N·m.
Les capacités sont respectées ; les projections moteur/couple sont contrôlées.

Cette recette désactive collisions, sommeil et amortissement, sans butées.
Elle ne qualifie pas les contacts d’une chaîne spatiale, ni une chaîne arbitraire,
ni une parité transitoire ou de coût avec Jolt. Pour une glissière chargée avec
contact axial, suivre [le parcours du rail retenu](LoadedRail3D.md).

Pour ajouter un plan à cette chaîne, suivre [le parcours de contact spatial](SpatialContacts3D.md).
