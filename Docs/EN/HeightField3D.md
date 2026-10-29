# Editing a height terrain

`HeightField3D` builds a fixed physical surface from a grid of heights.
`with_heights` and `with_holes` produce a new version without changing the
original terrain. `shape()` provides a snapshot usable by a fixed body.

In this fragment, `world` is an existing `Physics.World3D`:

```sx
var terrain = Physics.HeightField3D(3, 3,
    [0.0,0.0,0.0, 0.0,0.0,0.0, 0.0,0.0,0.0], 1.0, 1.0)
var floor = world.create_rigid_body(Physics.RigidBody3DSettings()
    ..body_type = Physics.BodyType3D.fixed ..shape = terrain.shape())
var raised = terrain.with_heights(0, 0, 2, 2, [0.05,0.05,0.05,0.05])
floor.set_shape(raised.shape())
```

An edit describes a region by its first sample `(column, row)`, followed by its
column and row counts. New values are row-major. The program chooses when to
publish a version with `set_shape`, at a safe simulation boundary. Publication
wakes bodies and replaces the shape revision; previous contacts end according
to the [world contract](World3D.md). Creating a version alone changes no body.

## Grid and holes

The constructor takes `columns`, `rows`, `heights`, `column_spacing` and
`row_spacing`, in meters. Sample `(column, row)` is located at
`(column × column_spacing, height, row × row_spacing)` in shape space.
At least two samples per axis, one finite height per sample and positive finite
spacing are required. Inputs are borrowed read-only and then copied; changing
source arrays does not change the terrain.

`holes:bool[]=[]` and `diagonal:HeightGridDiagonal3D.column_to_row` follow the
same rules as the [triangulated grid](Geometry3D.md): a hole removes triangles
using that vertex, and `first_to_opposite` chooses the other diagonal.
`with_holes(column, row, columns, rows, holes)` edits a region's mask. Closing
a hole restores its retained height; `with_heights` preserves the mask.

`columns()`, `rows()`, `column_spacing()`, `row_spacing()` and `diagonal()` read
configuration. `height(column, row)` reads a stored height even at a hole;
`is_hole(column, row)` reads its state. Invalid coordinates, missing data,
non-finite heights and fully holed edits are rejected. Removing the body removes
the whole surface.

## Versions and simulation

Old terrains, shapes and query results remain usable after an edit. Triangle
identities follow surviving face order in each shape; retain the corresponding
version when interpreting them. Height-only edits preserve topology, while
hole changes may renumber subsequent faces.

Terrain retains the front-face policy of fixed meshes. Abruptly moving relief
above a body does not recover a buried body; the consumer must choose an edit
compatible with its scene. The renderer owns its visual mesh; `shape()` does
not modify it.

Heights retain Silex `float` precision. No Jolt compression setting is exposed.
Grid triangles are evaluated from samples and topology; large-terrain cost
qualification remains separate from this editing API.

The [executable consumer](../../Tests/Consumer/Tests/HeightField3D.sx) covers
copies, old versions, publication, holes, waking, contacts and characters.

## Larger reliefs and query cost

Grids retain their samples and surviving face identities. Rays, translation
sweeps and contact generation select cells covered by conservative bounds.
Selection preserves face order and deterministic ties. Immutable surface bounds
and radius are computed at construction and replaced with each version.

Sphere, capsule and separated-box distances can also use a bound from a witness
triangle. Queries without a safe bound retain exhaustive traversal, including
some positive SAT distances and convex or CCD distances. A ray spanning the
entire relief can still inspect the whole grid. Editing constructs a new version;
it is not a constant-cost deformation. No universal constant query cost is promised.

The [selection consumer](../../Tests/Consumer/Tests/HeightFieldSelection3D.sx)
compares results against an exhaustive mesh: irregular reliefs, both diagonals,
holes, transforms, seven convex volumes and a65×65 sample grid.
