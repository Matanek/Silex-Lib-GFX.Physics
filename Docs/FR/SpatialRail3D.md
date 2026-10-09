# Porter une glissière hors du plan du bras

Une charnière au monde peut retenir un bras qui porte une glissière verticale,
avec une charge déportée sur le côté. Le montage transmet les forces et les
couples dans les trois dimensions ; la charge descend jusqu’au plan, puis
remonte après inversion du moteur.

Le [consommateur public](../../Tests/Consumer/Tests/SpatialRail3D.sx) exécute
16 parcours à 60/120 Hz, avec et sans plan, masses de charge 1/2 kg et déports
±0,8 m. Depuis la racine du workspace :

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialRail3D.sx
```

## Orienter la glissière

Le bras a son centre en `(0.5,0,0)`, masse 2 kg, inertie isotrope 0,4 kg·m².
La charnière d’axe Z le lie au monde, avec ancrage local `(-0.5,0,0)` et
moteur de vitesse nulle limité à 60 N·m. La sphère de rayon 0,15 m commence
en `(1,0,±0.8)`, inertie isotrope 0,2 kg·m². Seule cette sphère peut toucher
le plan Y=−0,22 m ; friction et restitution nulles, gravité Y=−9,81 m/s².

Les deux repères locaux de la glissière tournent de π/2 autour de Z : leur
axe X devient vertical Y. Le repère sur le bras est en `(0.5,0,±0.8)` ; celui
sur la charge est à son centre. La course initiale vaut zéro. Le moteur
avance à −0,2 m/s, inverse à +0,2 après 2/3 s, puis freine après 4/3 s,
avec une capacité de 40 N.

## Lire les réactions

`reaction_force()` de la glissière agit sur la charge. Sa force opposée agit
sur le bras au point mobile de la charge : le bras de levier inclut la course,
et ne se limite pas à l’ancrage local du rail. `reaction_torque()` est le
couple mondial supplémentaire ; la charnière reprend le moment hors du plan.

Le consommateur vérifie les bilans vectoriels de translation, rotation propre
et moment total en incluant l’impulsion et le point du contact. À l’arrêt
après libération, la glissière soutient le poids de la charge et la charnière
celui du montage ; le couple racine équilibre les moments des deux poids.
La profondeur minimale vaut 0,07 m avec le plan ou 2/15 m sans plan.

## Portée de la preuve

La recette `SpatialRail` de Silex-Benchmarks compare Native Debug/Release avec
Jolt épinglé et rejette 28 témoins corrompus par moteur/mode. Jolt fournit le
point et son levier, mais son impulsion normale est inférée du bilan : aucune
preuve normale indépendante. Les bornes acquises restent inchangées : bilan
linéaire 1e−5, spin 0,001, moment par pas 0,003, intégré 0,03, géométrie 0,005,
angle racine 0,02 et pénétration 0,003. Les preuves sont limitées à ce montage,
petites rotations, inerties isotropes et contact unique sans friction.
