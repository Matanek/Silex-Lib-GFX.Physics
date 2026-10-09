# Rotate a rail carrying a moving carriage

Combining a [hinge](Hinge3D.md) and a [motorized slider](SliderMotor3D.md)
lets a carriage move its mass along a rail that receives its reactions.
The rail is a dynamic body attached at the center of a fixed pivot: it can slow
when the load moves outward, or receive motor torque to maintain its rotation.
A kinematic rail instead imposes its motion independently of the forces received.

The [consumer test](../../Tests/Consumer/Tests/HingedRail3D.sx) builds this
assembly and checks both modes. From the workspace root:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/HingedRail3D.sx
```

## Build both constraints

The rail has a mass of 2 kg and isotropic inertia of 0.4 kg·m². The carriage
starts 1 m along its local X axis, with a mass of 1 or 2 kg and isotropic inertia
of 0.2 kg·m². The central hinge allows rotation around Z; the slider preserves
the shared orientation while allowing radial travel. Filters disable collisions
between the bodies in this witness.

Both bodies start at ±0.2 rad/s. The carriage's initial tangential velocity is
therefore ±0.2 m/s. Angular velocity alone does not define a consistent initial
state: the distant point must also follow the rotation.

`SliderMotor3D(0.6,2.0)` requests 0.6 m/s with a maximum force of 2 N.
After two thirds of a second, the target becomes −0.6 m/s, then zero after four
thirds. The motor accelerates, reverses and brakes; its capacity and the carriage
mass determine how far the carriage travels before each direction change.

## Choose free or driven rotation

Without a hinge motor, internal forces redistribute rotation. Total angular
momentum about the pivot stays close to its initial value: angular velocity
decreases as the radius grows. If the rail remains centered and the orientations
are aligned, total axial inertia is `0.4 + 0.2 + mass * radius²` in this recipe.

Setting `HingeMotor3D(omega,0.4)` on the hinge requests the initial velocity
with a maximum torque of 0.4 N·m. The motor then supplies an external effort:
angular momentum can change. The test checks that this change matches integrated
motor torque. The target can temporarily be exceeded under load; it does not
make the rail kinematic.

To measure total angular momentum about the pivot, add each body's `I * omega`
term and its orbital `mass * position.cross(velocity)` term. Include the rail's
orbital term even though its center should stay at the pivot: its small numerical
error must remain in the balance. Assembly energy is not conserved here because
the radial and hinge motors can supply or remove work.

## Verified scope

The consumer and pinned Jolt oracle cover 16 recipes over two seconds: two masses,
two directions, 60/120 Hz and a free or driven hinge. Native Debug and Release on
macOS ARM64 check reactions, budgets, anchors, radial reversal, final stopping
and redistribution of rotation.

The carriage and assembly linear balances, and the carriage spin balance, stay
below 2e−6 N·s or N·m·s. The angular momentum balance evaluated at final poses
allows 1e−4 N·m·s per step and 0.002 N·m·s cumulatively: integration, small anchor errors and pose
corrections affect orbital momentum evaluated at final positions. This bound does not describe exact discrete
conservation. Geometric errors stay below 0.001 m or rad; the angular velocity
difference between rail and carriage stays below 0.001 rad/s.

This recipe is planar, without gravity, contacts, damping, sleep, friction or
stops. It does not yet qualify an arbitrary spatial chain. Transient Silex/Jolt
forces and velocities can differ; outputs and differences are retained without
claiming phase or cost parity.
