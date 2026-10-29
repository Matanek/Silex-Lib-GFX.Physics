# Choosing and checking a 3D character

Virtual mode provides controlled movement with sliding, stairs and ground
following. Physical mode provides a capsule with real mass that receives
impacts and responds to the solver. Both can share the same world.

| Intent | Virtual | Physical |
| --- | --- | --- |
| Movement | `move` computes and applies controlled translation | `set_linear_velocity`, then `world.step` |
| Presence and contacts with other characters | `VirtualCharacter3D`, a registered kinematic capsule | `PhysicalCharacter3D`, a registered dynamic capsule |
| Query without presence | `CharacterMover3D.calculate_move` | Ordinary world queries |
| Slopes, walls, ceilings | Mover sliding and maximum slope | Rigid contacts and support classification after the step |
| Stairs and downward following | Step climbing and `floor_snap` | Physical response; no automatic step climbing |
| Pushing objects | Maximum force and effective mass at the contact point | Momentum exchange through dynamic mass |
| Weight on a support | Virtual mass and a separate gravity impulse | Dynamic body gravity |
| Translating or rotating support | Transport through successive support poses | Contacts, friction and support velocity at the contact point |
| Capsule changes | Feet preserved, atomic rejection on penetration | Feet and mass preserved; explicit penetration tolerance |
| Teleportation | `set_position` forgets the old support | `set_position` clears previous support state |
| Rotation | Upright mover capsule | Physical rotations locked, translations free |
| Zero duration | Pose, support and contacts preserved, no impulse | No step or contact update |

Input, jumping, cameras and animation belong to the application. An articulated
ragdoll is another physical representation; these controllers do not compute
procedural walking or animated balance.

## Fixed step ordering

For a physical character, provide the desired velocity before `world.step(delta)`
and read support after the step. For a virtual character, call `move` once per
step and retain its returned position; do not subsequently move its body as a
second controller. The mover consumes platform movement from successive known
poses: do not add platform velocity to the translation.

With the GFX plugin, `Physics3DStep.before_step` and `after_step` provide these
insertion points. The world is the `Physics.World3D` resource. The application
can then copy character position into its visual transform. The
[integrated consumer](../../Tests/Consumer/Tests/CharacterApplication3D.sx)
checks both modes, fixed stepping, pause/resume and world lifetime.

Movement operations borrow the world, so they also accept the GFX world
resource without copying or transferring ownership.

## Evidence and differences from Jolt

The independent `Silex-Benchmarks/Sources/Physics3D/CharacterRun.py` program
compares pinned Jolt 5.6.0 and the Silex consumer in Native Debug and Release:
weak push, capped push, virtual weight, a 70/30 kg collision, falling/rest and
standing up rejected under a ceiling. Absolute thresholds are 0.0001 for
velocity, capsule change and mass measurements, and 0.005 for rest.
Analytical balances also check both engines.

The [mover tests](../../Tests/Consumer/Tests/CharacterMover3D.sx),
[triangle terrain](../../Tests/Consumer/Tests/CapsuleTerrain3D.sx),
[convexes](../../Tests/Consumer/Tests/CharacterConvex3D.sx),
[mutable capsule](../../Tests/Consumer/Tests/CharacterResize3D.sx),
[dynamic exchanges](../../Tests/Consumer/Tests/CharacterDynamics3D.sx),
[physical mode](../../Tests/Consumer/Tests/PhysicalCharacter3D.sx) and
[character encounters](../../Tests/Consumer/Tests/CharacterInteractions3D.sx)
cover the other courses, filters, removals and lifetime guarantees.

Silex shares the push budget across children of one compound body, preventing
extra children from multiplying force. This does not claim to reproduce Jolt's
per-contact budget. The registered virtual character corresponds to Jolt's
`mInnerBodyShape` presence: physical bodies meet a kinematic obstacle, while
other virtual characters follow call order. Virtual support is probed even with
zero translation; in the Jolt witness, a common downward velocity first
establishes actual contact.

Mover penetration recovery remains bounded by a pass count. The deep-inclusion fixture
in an isolated box is covered; incompatible obstacles do not guarantee
an exit. Comparative measurements concern the executed macOS ARM64 native
profile, rather than a performance campaign or general qualification of every
solver assembly.

See the [mover](Character3D.md), [registered virtual](VirtualCharacter3D.md) and
[physical character](PhysicalCharacter3D.md) guides.
