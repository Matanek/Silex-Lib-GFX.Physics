# Retenir un rail chargé et libérer un contact

Un rail dynamique sur [charnière](Hinge3D.md) peut recevoir le poids d’un
chariot et les réactions de sa [glissière motorisée](SliderMotor3D.md).
Demander une vitesse angulaire nulle avec un couple suffisant permet ici de
retenir le rail près de son orientation horizontale initiale. Le chariot avance
vers une paroi, puis s’en éloigne lorsque sa vitesse cible est inversée.

Le [consommateur exécutable](../../Tests/Consumer/Tests/LoadedRail3D.sx)
construit ce parcours avec et sans paroi. Depuis la racine du workspace :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/LoadedRail3D.sx
```

## Dimensionner les moteurs pour la charge

Le rail commence immobile au pivot, avec une masse de 2 kg et une inertie
isotrope de 0,4 kg·m². Le chariot sphérique de rayon 0,25 m commence à 1 m
du pivot, avec une masse de 1 ou 2 kg et une inertie isotrope de 0,2 kg·m².
La gravité vaut `(0,-9.81,0)` ; la charnière tourne autour de Z et la glissière
suit X. Les collisions du pivot et du rail sont désactivées, celles du chariot
et de la paroi restent actives.

`HingeMotor3D(0.0,30.0)` demande zéro rad/s avec un plafond de 30 N·m.
Au repos, le couple nécessaire est proche de `mass * 9.81 * signed_radius`.
Le signe change lorsque le chariot se trouve de l’autre côté du pivot.
Dimensionner ce plafond selon le bras de levier ; un moteur saturé ne garantit
plus le maintien horizontal. Ce moteur en vitesse freine la rotation mais ne
ramène pas exactement à un angle cible : utiliser un servo de position pour
cette autre intention.

Le moteur de glissière demande 0,6 m/s vers l’extérieur avec une capacité de
2 N, puis inverse la cible après 2/3 s et demande zéro après 4/3 s. La paroi
se trouve à 1,4 m du pivot ; le centre du chariot la touche donc vers 1,15 m.
Le contact bloque l’avance sans annuler la commande du moteur. L’inversion
permet au chariot de quitter l’obstacle. Friction et restitution nulles isolent
la réponse normale de ce parcours.

## Lire les efforts après chaque pas

La réaction verticale de la glissière reprend le poids du chariot. Celle de
la charnière reprend les poids du chariot et du rail. À l’équilibre, les valeurs
attendues sont respectivement `mass * 9.81` et `(mass + 2) * 9.81` N.
Pendant l’accélération et l’impact, inclure aussi les variations de vitesse et
les impulsions de contact dans le bilan.

`world.write_contacts` expose les snapshots après `step`. L’impulsion appliquée
au second corps est `normal * normal_impulse + tangent_impulse` ; la première
reçoit son opposée. Le consommateur oriente ainsi l’impulsion vers le chariot
avant de vérifier `mass * velocity_change`. Les réactions de la glissière et
de la charnière sont des forces : les multiplier par la durée du pas pour
obtenir leurs impulsions.

## Portée vérifiée

Deux masses, deux côtés du pivot, 60/120 Hz, avec et sans paroi : 16 recettes
de deux secondes, qualifiées contre Jolt épinglé en Native Debug/Release sur
macOS ARM64. Les moteurs satisfont leurs plafonds de 2 N et 30 N·m ; le contact
doit réellement apparaître avec une impulsion significative, puis disparaître.
Le bilan linéaire et la rotation propre du chariot restent sous 1e−5 N·s ou
N·m·s, les erreurs géométriques sous 0,003 m ou rad, et l’angle sous 0,02 rad.
Les vitesses finales sont sous 0,005 m/s ou rad/s ; les erreurs de poids et de
couple final sous 0,05 N et N·m. La pénétration tolérée est de 0,003 m.

Silex mesure les impulsions de contact. La référence Jolt utilisée ne publie
pas leurs valeurs après résolution : sa composante normale est inférée du
mouvement et de la réaction de glissière, sans constituer un bilan normal
indépendant. Son état de contact et ses bilans verticaux, de rail et de rotation
sont contrôlés séparément. Les instants, durées et efforts transitoires des
contacts peuvent différer entre moteurs ; aucune parité de phase ou de coût.

Cette recette reste plane, sans amortissement, sommeil, friction ni butées
d’articulation. Elle ne qualifie pas une chaîne spatiale arbitraire. Pour un
rail qui tourne librement sous une charge mobile sans gravité, suivre
[la recette de redistribution de rotation](HingedRail3D.md).
