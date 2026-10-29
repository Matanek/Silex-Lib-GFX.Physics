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
if grounded { velocity.y = 0.0 }
let result = mover.calculate_move(world, position, velocity.multiply(delta), grounded)
position = result.position
grounded = result.grounded
velocity = result.clip_velocity(velocity)
```

Create `mover` once and reuse it. `half_height` is half the cylindrical segment:
the total height here is 1.7 m. `position` is the capsule centre, not its feet or
eyes. The result also exposes `ground_normal`, `stepped`, and `support()`. `clip_velocity`
removes velocity into encountered surfaces without adding artificial stair velocity.

The [executable consumer](../../Tests/Consumer/Tests/CharacterMover3D.sx) covers
motion and collisions. `World3D` in Silex-Examples adds variable jumping,
air control and an interpolated camera.

An inclined 4 by 4 grid is traversed in both directions, with positions
compared against Jolt Debug and Release within 5 mm. The
[terrain consumer](../../Tests/Consumer/Tests/CapsuleTerrain3D.sx) covers seams
and loss of support. `Physics3D/CapsuleTerrainScene.sx` in Silex-Examples lets
you try traversal and jumping. For grounded walking, reset vertical velocity
before applying motion: upward velocity retained after projection represents
an upward intention and disables downward floor following. Gravity and
jumping remain application rules.

A fixed convex hull can act as a slope, wall, step or ceiling. The
[convex consumer](../../Tests/Consumer/Tests/CharacterConvex3D.sx) checks sliding,
corners, slope and step limits, bounded overlap recovery and support loss.
The path on a `y=0.25z` slope agrees with Jolt Debug and Release within 5 mm in
both directions, including after horizontal rotation.
`Physics3D/CharacterConvexScene.sx` in Silex-Examples shows automatic walking;
Tab switches to manual control, WASD or arrows move the capsule, Space jumps
and R restarts.

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

For an isolated box, recovery uses the depth of the whole capsule and reaches
the same support as the equivalent convex hull: a 0.3/0.55 capsule centered at
y=0.8 inside a 4×2×4 box exits at y=1.852, including skin. The eight recovery
passes remain bounded; conflicting obstacles or a distant exit may still leave
residual penetration.

## Resize and teleport

`capsule()` reads the current dimensions. `try_resize(world, position, capsule)`
keeps the feet fixed and returns the new center, or `null` when the proposed
shape penetrates an obstacle. Rejection preserves both shape and support state:
the character remains crouched under a low ceiling. The query honors sensors,
filters and disabled bodies like ordinary movement.

```sx
if let resized = mover.try_resize(world, position, Physics.Capsule3D(0.3, 0.15)) {
    position = resized
}
```

The radius must remain greater than `skin`. Both height and width may change,
including while riding a platform. Call `mover.reset()` after teleporting or
before reusing the mover for another character to forget its previous support.
The application still owns `position`.
The [resize consumer](../../Tests/Consumer/Tests/CharacterResize3D.sx) covers atomic
rejection, ceilings, width, filtering and moving supports.

## Current scope

The mover is virtual and registers no rigid body. It reads current poses of
enabled boxes, spheres, capsules and compound children, plus the front faces
of fixed triangles and meshes, as well as fixed convex hulls. A kinematic support
keeps the character's point in its local frame between calls: translation and
rotation carry the capsule, even away from the centre of rotation. Call
`world.step(delta)` before `calculate_move`, and reuse the same mover with the
returned `grounded` state. The supplied translation remains the character's
own intent; the application does not add platform velocity. Jumping, removing
or disabling the support, or excluding it with the query filter ends the carry.
`result.support()` returns the body that supported this move, or `null`. As
with any body handle, check `is_valid()` before reusing it after possible
destruction.

Other encountered bodies remain obstacles at their current poses. The mover
does not push dynamic bodies or follow them as moving supports. The capsule
retains its vertical axis. Physical characters and
character-to-character interactions remain to be implemented. The package
imposes no jump or camera behavior. Do not share one instance concurrently
between threads.
