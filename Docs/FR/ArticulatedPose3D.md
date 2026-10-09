# Composer une épaule et un coude motorisés

Le [consommateur sans rendu](../../Tests/Consumer/Tests/ArticulatedPose3D.sx)
compose une épaule `SwingTwistConstraint3D` et un coude
`HingeConstraint3D`. Deux corps déportés transmettent leur poids jusqu’à
un support fixe. Les trois servos de l’épaule et le servo du coude changent
ensemble de cible, s’inversent puis se recentrent.

Le bras pèse 2 kg, l’avant-bras 1 ou 2 kg. Leurs inerties isotropes sont
respectivement 0,4 et 0,2 kg·m² ; les centres, ancrages et repères sont
excentrés et tournés. La gravité vaut −9,81 m/s² sur Y. Les plafonds sont
60 N·m par axe d’épaule et 40 N·m au coude. Raideurs/amortissements :
120/20 à l’épaule, 80/15 au coude. Chaque cible dure quatre secondes,
avec des pas de 60 ou 120 Hz.

## Repère d’effort pendant un pas

Une charnière portée par un corps mobile transporte son effort mémorisé
avec la rotation du premier corps. Ses axes de résolution angulaire sont
ceux du début du pas positif et restent cohérents pendant ce pas, y compris
après l’avancement des poses. Cela empêche un couple de l’ancien repère de
se mélanger au budget du nouveau moteur. Les signatures publiques sont
inchangées ; une mutation efface toujours les réactions devenues périmées.

Les couples vectoriels incluent l’alignement des axes. Leur composante moteur
est portée par l’axe du début du pas ; la vitesse relative est observée dans
le repère courant après le pas. Les forces moyennes d’ancrage peuvent avoir
été appliquées avant et après l’avancement des poses. Leur moment autour du
centre ne se reconstruit donc pas avec un seul bras de levier initial.

## Preuve et portée

Le témoin Jolt épinglé compare les équilibres en Native Debug/Release,
avec les mêmes cibles et budgets. Le comparateur vérifie la continuité,
les repères, les quantités de mouvement de chaque corps, les ancrages,
l’inversion et les équilibres de force et de couple. L’écart établi admissible
est de 0,005 rad pour chaque articulation, 0,003 rad/s en vitesse,
0,05 N et 0,05 N·m pour les réactions. Les écarts transitoires sont mesurés.

Un diagnostic séparé de Silex conserve les deux phases d’application des
forces et vérifie le bilan de rotation propre de chaque corps sous 0,001
kg·m²/s, sans modifier les sorties ordinaires. Le résidu mondial brut par pas
reste sous 0,003 kg·m²/s ; sa somme brute est une mesure de la chronologie et
des corrections de pose, pas une preuve indépendante de conservation exacte.
Le seuil cumulé initial de 0,03 n’était pas applicable à cette chaîne :
le même témoin refusait aussi Jolt. Les traces et la contre-épreuve restent
conservées avec les bilans séparés par phase.

Cette recette ne comporte ni contact ni auto-collision. Elle prépare une
pose articulée mais ne fournit pas encore de façade ragdoll, de hiérarchie
importée ni de parité transitoire générale. La destruction du bras invalide
les deux articulations ; l’avant-bras conserve son handle vivant.
