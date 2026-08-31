# Kinematic character movement

`CharacterMover2D` computes a safe capsule displacement without creating a
dynamic body for the character. The world stays read-only during calculation;
gameplay code then applies `applied_translation` to its ECS transform or other
character state.

```silex
use GFX.Physics
use STD.Math

var mover = Physics.CharacterMover2D(
    Physics.CharacterMover2DSettings()
        ..capsule = Physics.Capsule2D(
            Math.Vec2(0.0, -0.45),
            Math.Vec2(0.0, 0.45),
            0.3
        )
)

let result = mover.calculate_move(
    world,
    character_position,
    desired_velocity.multiply(delta_seconds)
)
character_position = character_position.add(result.applied_translation)
```

The result also reports remaining translation, touched colliders, collision
planes, iteration counts, and whether the capsule started overlapped. Sensors
are ignored by default. `query_filter` limits collision categories;
`include_sensors` explicitly treats sensors as obstacles.

## Separate plane control

`collect_planes` gathers planes around the current capsule, `solve_planes`
depenetrates and constrains a translation, and `clip_vector` removes motion
into active planes. This separation lets a gameplay controller choose what
counts as ground, a walkable wall, or an overly steep slope.

Work is bounded by `maximum_iterations` and `maximum_plane_iterations`.
`tolerance` must be finite and strictly positive. One-sided chains retain their
winding convention.

## Visual example

```text
silex run Silex-Examples/Sources/CharacterMover2D.sx --release
```

The demo drives a capsule across a floor, slope, step, concave corner,
trampoline, pushable dynamic crate, and moving kinematic platform. Arena walls
retain physical objects. It is owned by the public `Silex-Examples` catalog.
Use `A`/`D` or the arrow keys to move, `Space` to jump, and `R` to reset.
