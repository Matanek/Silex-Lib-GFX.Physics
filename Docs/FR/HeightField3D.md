# Modifier un terrain par hauteurs

`HeightField3D` construit une surface physique fixe depuis une grille de hauteurs.
`with_heights` et `with_holes` produisent une nouvelle version, sans modifier le
terrain initial. `shape()` fournit un instantané utilisable par un corps fixe.

Dans ce fragment, `world` est un `Physics.World3D` existant :

```sx
var terrain = Physics.HeightField3D(3, 3,
    [0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0], 1.0, 1.0)
var floor = world.create_rigid_body(Physics.RigidBody3DSettings()
    ..body_type = Physics.BodyType3D.fixed ..shape = terrain.shape())
var raised = terrain.with_heights(0, 0, 2, 2, [0.05,0.05,0.05,0.05])
floor.set_shape(raised.shape())
```

L'édition décrit une zone par son premier échantillon `(column, row)`, puis son
nombre de colonnes et de lignes. Les nouvelles valeurs sont rangées par lignes.
Le programme décide quand publier la version avec `set_shape`, à une frontière
sûre de sa simulation. Cette publication réveille les corps et remplace la
révision de forme ; les contacts précédents se terminent selon le contrat du
[monde](World3D.md). Créer une version seule ne change aucun corps.

## Grille et trous

Le constructeur prend `columns`, `rows`, `heights`, `column_spacing` et
`row_spacing`, en mètres. L'échantillon `(column, row)` se trouve en
`(column × column_spacing, height, row × row_spacing)` dans le repère de la forme.
Au moins deux échantillons par axe, une hauteur finie par échantillon et des
espacements positifs finis sont requis. Les entrées sont empruntées en lecture
puis copiées ; modifier les tableaux sources ne change pas le terrain.

`holes:bool[]=[]` et `diagonal:HeightGridDiagonal3D.column_to_row` ont les mêmes
règles que [la grille triangulée](Geometry3D.md) : un trou retire les triangles
utilisant ce sommet, et `first_to_opposite` choisit l'autre diagonale.
`with_holes(column, row, columns, rows, holes)` change le masque d'une zone.
Fermer un trou retrouve la hauteur conservée ; `with_heights` conserve le masque.

`columns()`, `rows()`, `column_spacing()`, `row_spacing()` et `diagonal()` lisent
la configuration. `height(column, row)` lit la hauteur stockée, même pour un trou ;
`is_hole(column, row)` lit son état. Les coordonnées invalides, données manquantes,
hauteurs non finies et éditions entièrement trouées sont refusées. Retirer le
corps permet de retirer toute la surface.

## Versions et simulation

Les anciens terrains, formes et résultats de requête restent utilisables après
une édition. Les identités de triangles suivent l'ordre des faces survivantes
de chaque forme ; les conserver avec la version correspondante. Une édition
des seuls niveaux conserve la topologie, tandis qu'un changement de trous peut
changer la numérotation des faces suivantes.

Le terrain garde la politique de face avant des maillages fixes. Un déplacement
brusque du relief au-dessus d'un corps ne constitue pas une récupération de corps
enterré ; le consommateur doit choisir une édition compatible avec sa scène.
Le renderer conserve la propriété de son maillage visuel ; `shape()` ne le modifie pas.

Les hauteurs restent exactes à la précision `float` de Silex. Aucun réglage de
compression Jolt n'est exposé. Les triangles de grille sont évalués depuis les
échantillons et la topologie ; la qualification des coûts des grands reliefs
reste distincte de cette API d'édition.

Le [consommateur exécutable](../../Tests/Consumer/Tests/HeightField3D.sx) couvre
copies, anciennes versions, publication, trous, réveil, contacts et personnage.

## Reliefs étendus et coût des requêtes

Les grilles conservent leurs échantillons et les identités des faces survivantes.
Rayons, balayages par translation et génération des contacts sélectionnent les
cellules couvertes par des bornes conservatives. La sélection conserve l'ordre
des faces ; les égalités restent déterministes. Les bornes et le rayon de la
surface immuable sont calculés à sa construction, puis remplacés avec sa version.

Les distances sphère, capsule et boîte séparée peuvent aussi utiliser une borne
issue d'un triangle témoin. Les requêtes sans borne sûre gardent le parcours
exhaustif, notamment certaines distances SAT positives et les distances convexes
ou CCD. Un rayon couvrant tout le relief peut encore examiner toute la grille.
L'édition reste une opération de construction de version, pas une déformation
à coût constant. Aucun coût constant universel n'est garanti.

Le [consommateur de sélection](../../Tests/Consumer/Tests/HeightFieldSelection3D.sx)
compare les résultats à un maillage exhaustif : relief irrégulier, deux diagonales,
trous, transforms, sept volumes convexes et grille de65×65 sommets.
