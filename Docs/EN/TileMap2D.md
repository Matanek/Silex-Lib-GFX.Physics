# Tile map collisions

`Physics.TileMapCollider2D` is an ECS component for an entity carrying
`Scene2D.TileMap` and `Scene2D.Transform`. Install `Plugins.Physics2D`, then:

```sx
world.spawn(ECS.EntityRecipe()
    ..with(Scene2D.Transform())
    ..with(map)
    ..with(Physics.TileMapCollider2D()))
```

Every occupied cell is solid, regardless of its image index. Keep decoration,
coins and hazards on separate layers. The constructor accepts a
`collision_filter`. This component owns the generated `PhysicsBody2D` on that
entity; do not add another one.

Horizontal runs are merged, then runs with equal width and column are joined
across successive rows. Construction visits the grid in linear time and
preserves holes. A full map produces one fixed body and one collider, with no
entity per tile. Rectangles are converted to meters using the plugin's
`scene_units_per_meter`. Translation and rotation are supported; global scale
must remain `(1, 1)`.

The plugin rebuilds shapes when content or the filter changes, before body
reconciliation in `post_update`. Stable frames do not traverse cells and retain
body identity. Edits during physics callbacks take effect on the next frame.
Rebuilding replaces the body: do not retain its handles across edits.
`enable(false)` suspends the body; removing the component, map, transform or
entity destroys its collisions. An empty map has no implicit shape.
Rendering visibility does not affect collisions.

For a standalone physics world, `collider.body(map, scene_units_per_meter)`
returns the `PhysicsBody2D` recipe; `collider.rectangles(map)` returns cell-space
rectangles (`column`, `row`, `columns`, `rows`). Merging covers filled rectangles;
slopes, one-way surfaces and partial tile collisions are outside this contract.
Editing a cell currently rebuilds the whole map's collision geometry. Split
very large editable worlds into multiple maps before targeting streaming.

[Back to GFX.Physics](README.md)
