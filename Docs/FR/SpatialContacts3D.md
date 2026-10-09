# Mettre une chaîne spatiale en contact avec un plan

La [chaîne à deux charnières perpendiculaires](SpatialHinges3D.md) peut porter
une charge sphérique jusqu’à un plan horizontal, puis libérer le contact lors
de l’inversion du moteur. Les réactions des liaisons et l’impulsion du contact
participent ensemble au soutien de la charge.

Le [consommateur exécutable](../../Tests/Consumer/Tests/SpatialContacts3D.sx)
vérifie le parcours avec et sans plan depuis la racine du workspace :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialContacts3D.sx
```

## Disposer le contact

Les corps, axes Z/X, ancrages, masses et inerties reprennent la recette spatiale.
La charge est une sphère de rayon 0,15 m, centrée initialement en `(1,0,±0.8)`.
Un corps fixe porte `Shape3D.plane(Plane3D(Vec3(0,1,0),-0.22))` : son plan
est à Y=−0,22 m. Désactiver les collisions du pivot et du bras ; laisser celles
de la charge actives. Friction et restitution valent zéro des deux côtés.
Les moteurs disposent de 60/40 N·m : le premier retient le bras, le second
avance à ±0,2 rad/s, inverse après 2/3 s et freine après 4/3 s.

## Inclure le point d’application

Après `World3D.step`, `write_contacts` fournit des snapshots du dernier pas.
Leur normale pointe du premier corps vers le second. L’impulsion
`normal * normal_impulse + tangent_impulse` s’applique au second ; inverser
son signe pour le premier. `write_points` fournit la position et les impulsions
de chaque point du manifold. Pour plusieurs points, sommer leurs moments
individuels plutôt que multiplier le point moyen par l’impulsion totale.

Le bilan linéaire ajoute l’impulsion de contact. Le bilan de rotation propre
ajoute `contact_lever.cross(impulse)` autour du centre de masse au moment de
l’application. Le bilan du moment cinétique total ajoute
`point.position.cross(impulse)` autour de l’origine monde. Les forces et
couples des charnières gardent [leurs conventions](SpatialHinges3D.md).

Dans cette recette Silex, le point sphère/plan est recalculé sur la normale du
centre de la sphère : le bras de levier est `(0,-radius-separation/2,0)` et
l’impulsion sans friction ne crée pas de rotation propre. La position publique
reste nécessaire au moment total. Cette reconstruction dépend de cette forme
et de ce plan ; les poses de fin de pas peuvent déjà inclure des corrections.
Un contact conservé par un autre moteur peut avoir un bras de levier légèrement
décalé : ne pas supposer une impulsion centrale dans une comparaison.

## Portée vérifiée

Deux masses, deux déports ±0,8 m, 60/120 Hz et présence/absence du plan donnent
16 parcours de deux secondes. Silex et Jolt épinglé passent en Native
Debug/Release sur macOS ARM64. Avec le plan, le pic d’impulsion dépasse
0,1 N·s ; le moteur inverse et le contact est libéré avant le repos final.
L’excursion dépasse 0,07 rad, les deux sens de vitesse 0,15 rad/s.

Les bornes sont 1e−5 N·s pour le bilan linéaire, 0,001 N·m·s pour la rotation
propre, 0,003 par pas et 0,03 cumulés pour le moment total. Ancrages et axes
restent sous 0,005 m/rad, pénétration sous 0,003 m et angle racine sous
0,02 rad. Vitesses finales sous 0,005 m/s ou rad/s ; erreurs de poids/couple
sous 0,05 N/N·m. Les capacités et projections des moteurs sont contrôlées.

Silex publie les impulsions résolues. L’oracle Jolt infère l’impulsion normale
depuis le bilan linéaire de la charge et observe le point pré-solveur via son
listener ; cette inférence ne constitue pas une preuve indépendante du bilan
normal ou du moment de contact. Les bornes incluent intégration et corrections
de pose, sans conservation discrète exacte ni parité de phase ou de coût.
Cette recette ne qualifie pas friction, butées, sommeil, grandes rotations,
inerties anisotropes, contacts multiples ou chaînes arbitraires.

## Maintenir une poussée contre le plan

Conserver la commande secondaire de vitesse pendant trois secondes bloque la
charge près de `asin(0,07/0,8)`, soit 0,0876 rad, avec un moteur racine de
vitesse nulle. Les contacts persistants participent au solveur commun avant
l’intégration des articulations ; leur effort accumulé traverse les phases sans
être appliqué deux fois. Les snapshots conservent le point utilisé lors de la
résolution, qui peut précéder la pose finale. Une téléportation par `set_transform`
invalide l’appui mémorisé et impose une détection depuis la nouvelle pose.

Le consommateur inclut poussée prolongée, changement de pas, désactivation,
filtrage, révision de forme et réutilisation d’un slot de corps. `set_shape`
recalcule la masse et l’inertie depuis la densité ; pour conserver des propriétés
explicites dans cette fixture, appeler ensuite `set_mass_properties`.

La recette publique `SustainedSpatialContacts` dans Silex-Benchmarks conserve
les mêmes masses, déports, pas et bornes de bilan sur 16 parcours de trois secondes.
Avec le plan, la charge reste bloquée, les moteurs respectent 60/40 N·m et les
vitesses convergent sous 0,005. Le servo d’angle est un ressort à capacité finie ;
sa déformation sous pression n’est pas une fixation rigide. Ces preuves restent
limitées à cette sphère, ce plan, petits angles et inerties isotropes.
