# Debug draw physique

`World2D.write_debug_snapshot` transforme l’état du dernier pas terminé en une
liste autonome de lignes, cercles et labels. Le snapshot ne conserve ni handle
interne, ni callback, ni verrou sur le monde : il peut être rendu plus tard ou
à une cadence différente de la simulation.

```silex
use GFX.Physics

var snapshot = Physics.World2DDebugSnapshot()
let settings = Physics.World2DDebugSettings()
    ..bounds = true
    ..contacts = true
    ..contact_normals = true
    ..labels = true

world.step(1.0 / 60.0)
world.write_debug_snapshot(settings, snapshot)

var drawing = Physics.World2DDebug.canvas(snapshot)
var scene_canvas = Physics.World2DDebug.scene_canvas(snapshot)
```

Les couches couvrent les formes, joints, AABB, centres de masse, labels,
contacts, normales, impulsions, îlots et couleurs du graphe de contraintes.
`World2DDebugTheme` rend chaque couleur modifiable. Une
`World2DDebugRegion(lower, upper)` optionnelle élimine les primitives hors de
la zone visible avant leur écriture.

Le réglage par défaut n’active que les formes et les joints. Mettre `enabled` à
`false` vide le snapshot sans parcourir le monde. Réutiliser le même
`World2DDebugSnapshot` conserve ses capacités de stockage ; après une première
écriture de taille suffisante, `storage_growth_count()` reste stable tant que
le nombre de primitives n’augmente pas.

Le renderer écrit soit dans un `GFX.Canvas.Canvas` fourni avec `draw`, soit
dans un nouveau Canvas via `canvas`, soit dans un composant
`GFX.Scene2D.Canvas` via `scene_canvas`. Il reste un outil de diagnostic et ne
remplace pas la représentation visuelle du jeu.

La preuve consommateur est
[`DebugDraw.sx`](../../Tests/Consumer/Tests/DebugDraw.sx). Deux exemples visuels
séparent les intentions de diagnostic. Le premier emploie les mètres, la
gravité `(0, -9.81) m/s²` et un pas fixe de 60 Hz ; des corps chutent en continu
sur une rampe, une chaîne et un sol. Ses labels fixes vivent dans un Canvas
vectoriel immuable, tandis que le Canvas géométrique est réécrit uniquement
après un pas physique. Le second anime séparément les huit familles de joints,
leurs bounds, centres de masse et couleurs de graphe. Chaque exemple affiche
sa cadence avec `FPSPanel` :

```text
silex run Silex-Examples/Sources/PhysicsDebugDraw2D/Main.sx --release
silex run Silex-Examples/Sources/PhysicsJointDebugDraw2D/Main.sx --release
```
