# Îlots actifs et sommeil

`World2D` groupe les corps dynamiques en îlots internes déterministes. Les
consommateurs observent seulement `is_awake()` et `awake_body_count()`.

```silex
world.step(1.0 / 60.0)
print(body.is_awake())
print(world.awake_body_count())
```

Les corps éveillés sont rassemblés par identité stable dans une liste
réutilisable. L’intégration parallèle découpe le même ordre logique. Un
union-find privé connecte joints et contacts généraux, puis range les corps de
chaque îlot de façon déterministe.

Les îlots articulés ou de formes générales dorment atomiquement. Les contacts
primitifs boîte/cercle autorisent un sommeil local : les corps enfouis quittent
le chemin chaud tandis que la surface reste active. Un impact significatif ne
réveille d’abord que le corps touché et un cooldown empêche une propagation
immédiate à toute la pile.

Créer ou détruire un corps sans rapport ne réveille pas les dormeurs. Détruire
un membre reconstruit les données dérivées tout en préservant l’état des handles
survivants.

```text
silex test Packages/GFX.Physics/Tests/Consumer/Tests/Islands.sx
```
