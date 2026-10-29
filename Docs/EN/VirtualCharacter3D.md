# Registered virtual character

`VirtualCharacter3D` combines the [capsule mover](Character3D.md) with a kinematic
presence in the world. Other characters and ordinary queries see the capsule;
its own mover excludes that presence.

```sx
var character = world.create_virtual_character(
    Physics.CharacterMover3DSettings() ..max_push_force = 100.0,
    Math.Vec3(0.0, 0.852, 0.0))
var result = character.move(world, velocity.multiply(delta), delta)
velocity = result.clip_velocity(velocity)
```

The character owns its position, exposed by `position()`. `move` updates its
capsule once; the world step adds no second displacement. The kinematic body
keeps zero velocity as a pose-controlled presence. `mass` transfers weight and
`max_push_force` bounds mover pushes; physical bodies keep their ordinary reactions
against the kinematic presence. [Physical mode](PhysicalCharacter3D.md) serves
characters whose own dynamic mass must receive recoil in the rigid solver.

`is_grounded()`, `ground_normal()`, `support()`, `contact_count()` and `contact(index)`
describe the last move. Zero duration preserves pose and contacts.
`try_resize(world, capsule)` keeps the feet fixed and rejects overlap;
`set_position(position)` teleports and forgets old support. `body()` provides the
presence for queries and attachments. Keep an upright capsule and let the character
author its movement.

The third `create_virtual_character` argument is the presence's `CollisionFilter3D`.
Categories, reciprocal masks and groups apply to encounters; the mover settings'
query filter still selects obstacles and sensor observations.
Virtual/virtual encounters follow `move` call order, as sequential driven-character
updates do. Contacts identify peers through ordinary body handles.

The world owns the body. `destroy_virtual_character(character)`, direct body
removal and world disposal invalidate the handle. `move` and `try_resize` reject
a foreign world. The [standalone mover](Character3D.md) remains available when
no character presence is wanted in ordinary world queries.

[Interaction consumer](../../Tests/Consumer/Tests/CharacterInteractions3D.sx): presence,
queries, no double integration, three mode combinations, masks, pause and lifetime.
