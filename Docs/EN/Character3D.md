# Move a 3D character

`CharacterMover3D` moves an upright capsule through a `World3D`: it slides along
walls, stops at ceilings, limits slopes and climbs allowed steps. The application
keeps the centre position and velocity and owns gravity, jumping, input and camera.

## Apply motion

In a fixed timestep loop, this fragment assumes a `world`, `position`, `velocity`,
`grounded` state and a `delta` interval:

```sx
var mover = Physics.CharacterMover3D(Physics.CharacterMover3DSettings()
    ..radius = 0.3 ..half_height = 0.55 ..step_height = 1.2)
let result = mover.calculate_move(world, position, velocity.multiply(delta), grounded)
position = result.position
grounded = result.grounded
velocity = result.clip_velocity(velocity)
```

Create `mover` once and reuse it. `half_height` is half the cylindrical segment:
the total height here is 1.7 m. `position` is the capsule centre, not its feet or
eyes. The result also exposes `ground_normal` and `stepped`. `clip_velocity`
removes velocity into encountered surfaces without adding artificial stair velocity.

The [executable consumer](../../Tests/Consumer/Tests/CharacterMover3D.sx) covers
motion and collisions. `World3D` in Silex-Examples adds variable jumping,
air control and an interpolated camera.

## Configure support

- `max_slope_angle` is in radians, strictly between 0 and π/2; default 45°.
- `step_height` defaults to 0.4 m; zero disables stair climbing.
- `step_forward` defaults to 0.18 m: lookahead distance for finding walkable
  support beyond the capsule’s rounded edge. The probe never adds horizontal
  travel to the requested motion, even at low speed.
- `floor_snap` defaults to 0.5 m: maximum downward support-following distance.
- `skin` defaults to 0.002 m and must be strictly between zero and the radius.
- `filter` uses `QueryFilter3D` and excludes sensors by default.

Stair climbing requires previous support and no upward motion. The capsule must
fit below ceilings while rising and find walkable support on its way down.
Floor snapping is disabled while jumping upwards. An unwalkable slope cannot
turn horizontal pressure into ascent. Initial overlap recovery uses bounded
passes; a capsule deeply enclosed in geometry is not guaranteed to escape.

## Current scope

The mover is virtual and registers no rigid body. It reads current poses of
enabled boxes, spheres, capsules and compound children. Encountered bodies are
treated as stationary obstacles for that call: the mover does not push them or
carry the character along with moving supports yet. Update the world before
moving the character when obstacles move.

The capsule retains its shape and vertical axis. Physical characters, shape
changes, character-to-character interactions and moving supports remain to be
implemented. The package imposes no jump or camera behavior. Do not share one
instance concurrently between threads.
