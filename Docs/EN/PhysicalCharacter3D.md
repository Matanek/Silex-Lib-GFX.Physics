# Physical 3D character

`PhysicalCharacter3D` uses a dynamic capsule owned by the world: gravity,
contacts and its mass participate in the rigid solver. Physical rotations are
locked; an offset force can translate the character without tipping it over.
The application chooses its velocity and jump rules.

This fragment assumes an existing `world` and `delta`.

```sx
var character = world.create_physical_character(
    Physics.PhysicalCharacter3DSettings() ..mass = 70.0,
    Math.Vec3(0.0, 1.2, 0.0))
character.set_linear_velocity(Math.Vec3(2.0, character.linear_velocity().y, 0.0))
world.step(delta)
let grounded = character.is_grounded()
```

The world updates contacts and support after each step. `ground_state()`
distinguishes `grounded`, `steep`, `touching` and `airborne`. `ground_normal()`,
`ground_velocity()` and `support()` describe support; velocity includes rotation
at the contact point. `contact_count()` and `contact(index)` expose contacts
from the last step. A zero-duration step preserves this state.

`max_slope_angle` defaults to 45° and `support_distance` to 0.02 m, retaining support
within the contact margin. `mass`, `friction`, `gravity_scale`, `collision_filter`
and `allow_sleep` configure the body. Geometric stairs and snapping belong to the
[virtual mover](Character3D.md); physical mode uses rigid reactions and recoil.

## Resize and reposition

`try_resize(world, capsule, max_penetration:0.005)` preserves feet and mass and
rejects a shape exceeding the stated penetration tolerance. Rejection changes
neither pose nor shape. Angular locking survives shape and mass changes.
`set_position(position)` teleports and forgets previous support.

`body()` provides the body for forces, impulses, attachments and queries.
Keep an upright capsule and use `try_resize` for its dimensions; arbitrarily
replacing its shape bypasses the character contract.

The world owns the body. `world.destroy_physical_character(character)` removes
it with its constraints, invalidating the handle. Direct removal with
`destroy_rigid_body(character.body())` and world disposal also invalidate it.
Removing a support makes `support()` return null and clears grounded status.
Contact handles follow the world's usual validity rules.

[Executable consumer](../../Tests/Consumer/Tests/PhysicalCharacter3D.sx): falling,
rest, mass/recoil, slopes, platforms, resizing, filters and lifetime.
