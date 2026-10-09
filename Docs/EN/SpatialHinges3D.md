# Carry a load through two perpendicular hinges

A fixed → arm → payload chain can transmit weight through two perpendicular
[hinges](Hinge3D.md). The first motor holds the arm about Z; the second holds
or moves the payload about X. The Z offset also produces an X torque at the
pivot: the hinge’s locked components participate in supporting this load.

The [executable consumer](../../Tests/Consumer/Tests/SpatialHinges3D.sx)
checks holding, then driving, reversal and braking. From the workspace root:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialHinges3D.sx
```

## Place bodies and frames

The arm has mass 2 kg, isotropic inertia 0.4 kg·m² and initial center
`(0.5,0,0)` m. The payload has mass 1 or 2 kg, inertia 0.2 kg·m² and center
`(1,0,±0.8)` m. All initial rotations are identity and velocities zero.
Gravity is `(0,-9.81,0)`.

The first hinge connects the fixed pivot to the arm at world `(0,0,0)`.
Its arm-local anchor is `(-0.5,0,0)`; axis Z and normal X are the defaults.
The second connects arm to payload at world `(1,0,0)`: local anchors
`(0.5,0,0)` on the arm and `(0,0,∓0.8)` on the payload. Both local axes
are X and both local normals Y.

`HingeMotor3D(0.0,60.0)` holds the arm with capacity 60 N·m. The second motor
has capacity 40 N·m: it requests zero, or ±0.2 rad/s, reverses after 2/3 s,
then requests zero after 4/3 s. A velocity motor brakes without restoring a
precise angle; choose the [position servo](HingePosition3D.md) for that intent.
Size the capacity for weight and acceleration.

## Interpret reactions

`reaction_force()` and `reaction_torque()` return a force and torque in world
space applied to the second body. The first receives their opposites. Torque
does not include the moment of the anchor force: add
`lever_arm.cross(reaction_force)` to obtain total torque about the mass center.
Use the lever arm when the impulse is applied, before step integration.

At rest the second force supports payload weight; the first supports both
weights. With initial poses the first torque is approximately
`(-mass*9.81*z,0,(1+mass)*9.81)` N·m and the second
`(-mass*9.81*z,0,0)` N·m, where `z` is the signed payload offset. The first
motor only provides the Z component; its locked axes transmit X torque.
`motor_torque()` is a scalar along the joint axis, while `reaction_torque()`
also includes locked components. After motion, calculate equilibrium using
current positions and lever arms.

During motion, spin balance includes these anchor moments. Total angular
momentum also includes `position.cross(mass*velocity)` for each body. Gravity
and the pivot reaction are external; internal second-hinge reactions cancel
in this balance.

## Verified scope

Two masses, two offsets, 60/120 Hz and holding/driving give 16 two-second
recipes. Silex and pinned Jolt independently qualify in Native Debug/Release
on macOS ARM64. Linear balances stay below 1e−5 N·s; rotational balances
below 0.001 N·m·s per step and 0.01 N·m·s cumulatively for total momentum.
These bounds account for integration and pose corrections; they do not claim
exact discrete conservation.

Anchors and axes stay below 0.005 m/rad; arm and held-payload angles below
0.02 rad. Driving must exceed 0.08 rad and reach both speed signs beyond
0.15 rad/s. Final speeds stay below 0.005 m/s or rad/s, weight and torque
errors below 0.05 N and N·m. Capacities and motor/torque projections are checked.

This recipe disables collisions, sleep and damping, with no stops. It does
not qualify contacts in a spatial chain, arbitrary chains, or transient/cost
parity with Jolt. For a loaded slider with axial contact, follow
[the held-rail recipe](LoadedRail3D.md).
