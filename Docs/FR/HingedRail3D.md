# Faire tourner un rail portant un chariot mobile

Associer une [charnière](Hinge3D.md) et une [glissière motorisée](SliderMotor3D.md)
permet au chariot de déplacer sa masse le long d’un rail qui reçoit ses réactions.
Le rail est un corps dynamique attaché au centre du pivot fixe : il peut ralentir
lorsque la charge s’éloigne, ou recevoir le couple d’un moteur pour maintenir sa
rotation. Un rail cinématique impose au contraire son mouvement indépendamment
des efforts reçus.

Le [test consommateur](../../Tests/Consumer/Tests/HingedRail3D.sx) construit cet
assemblage et vérifie les deux modes. Depuis la racine du workspace :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/HingedRail3D.sx
```

## Construire les deux liaisons

Le rail a une masse de 2 kg et une inertie isotrope de 0,4 kg·m². Le chariot
commence à 1 m sur son axe local X, avec une masse de 1 ou 2 kg et une inertie
isotrope de 0,2 kg·m². La charnière centrale laisse tourner autour de Z ; la
glissière conserve l’orientation commune et laisse la course radiale libre.
Les filtres désactivent les collisions entre les corps de ce témoin.

Les deux corps commencent à ±0,2 rad/s. La vitesse tangentielle initiale du
chariot vaut donc ±0,2 m/s. Une vitesse angulaire seule ne suffit pas à définir
un état initial cohérent : le point éloigné doit aussi suivre la rotation.

`SliderMotor3D(0.6,2.0)` demande 0,6 m/s avec une force maximale de 2 N.
Après deux tiers de seconde, la cible devient −0,6 m/s, puis zéro après quatre
tiers. Le moteur accélère, inverse et freine ; sa capacité et la masse du chariot
déterminent la distance parcourue avant chaque changement de sens.

## Choisir une rotation libre ou motorisée

Sans moteur de charnière, les efforts internes changent la répartition de la
rotation. Le moment cinétique total autour du pivot reste proche de sa valeur
initiale : lorsque le rayon augmente, la vitesse angulaire diminue. Si le rail
reste centré et si les orientations sont alignées, l’inertie axiale totale vaut
`0.4 + 0.2 + mass * radius²` dans cette recette.

Configurer `HingeMotor3D(omega,0.4)` sur la charnière demande la vitesse initiale
avec un couple maximal de 0,4 N·m. Le moteur fournit alors un effort extérieur :
le moment cinétique peut changer. Le test vérifie que ce changement correspond
au couple moteur intégré. Une cible peut être temporairement dépassée sous la
charge ; elle ne rend pas le rail cinématique.

Pour mesurer le moment cinétique total autour du pivot, additionner les termes
`I * omega` des corps et les moments orbitaux `mass * position.cross(velocity)`.
Le moment du rail est inclus même si son centre devrait rester au pivot : son
petit écart numérique ne doit pas disparaître du bilan. L’énergie de l’ensemble
n’est pas conservée ici, car le moteur radial et le moteur de charnière peuvent
fournir ou retirer du travail.

## Portée vérifiée

Le consommateur et l’oracle Jolt épinglé couvrent 16 recettes sur deux secondes :
deux masses, deux sens, 60/120 Hz et charnière libre ou motorisée. Native Debug et
Release sur macOS ARM64 vérifient les réactions, les budgets, les ancrages,
l’inversion radiale, l’arrêt final et la redistribution de rotation.

Le bilan linéaire du chariot et de l’ensemble, ainsi que le bilan de rotation
propre du chariot, restent sous 2e−6 N·s ou N·m·s. Le bilan de moment cinétique
sur les poses de fin de pas tolère 1e−4 N·m·s par pas et 0,002 N·m·s cumulés :
l’intégration, les petits écarts d’ancrage et les corrections de pose affectent
le moment orbital évalué sur les positions finales.
Cette borne ne décrit pas une égalité exacte de conservation discrète.
Les erreurs géométriques restent sous 0,001 m ou rad, l’écart de vitesse angulaire
entre rail et chariot sous 0,001 rad/s.

Cette recette est plane, sans gravité, contacts, amortissement, sommeil,
friction ni butées. Elle ne qualifie pas encore une chaîne spatiale quelconque.
Les efforts et vitesses transitoires Silex/Jolt peuvent différer ; les sorties
et leurs écarts sont conservés sans revendiquer de parité de phase ou de coût.
