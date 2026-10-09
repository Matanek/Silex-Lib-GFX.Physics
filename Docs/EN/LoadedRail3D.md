# Hold a loaded rail and release a contact

A dynamic rail on a [hinge](Hinge3D.md) can receive a carriage's weight and
the reactions of its [driven slider](SliderMotor3D.md). Requesting zero angular
speed with sufficient torque holds this rail near its initial horizontal
orientation. The carriage advances towards a wall, then retreats when its
target speed is reversed.

The [executable consumer](../../Tests/Consumer/Tests/LoadedRail3D.sx) constructs
this path with and without the wall. From the workspace root:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/LoadedRail3D.sx
```

## Size the motors for the load

The rail starts at rest at the pivot, with mass 2 kg and isotropic inertia
0.4 kg·m². The spherical carriage has radius 0.25 m and starts 1 m from the
pivot, with mass 1 or 2 kg and isotropic inertia 0.2 kg·m². Gravity is
`(0,-9.81,0)`; the hinge rotates about Z and the slider follows X. Pivot and
rail collisions are disabled; carriage and wall collisions remain enabled.

`HingeMotor3D(0.0,30.0)` requests zero rad/s with capacity 30 N·m. At rest,
the required torque is close to `mass * 9.81 * signed_radius`. Its sign changes
when the carriage is on the other side of the pivot. Size the capacity for
the lever arm; a saturated motor no longer guarantees horizontal holding.
This velocity motor brakes rotation but does not return exactly to a target
angle: use a position servo for that other intention.

The slider motor requests 0.6 m/s outwards with capacity 2 N, then reverses
the target after 2/3 s and requests zero after 4/3 s. The wall is 1.4 m from
the pivot, so the carriage center touches it near 1.15 m. Contact blocks
advance without cancelling the motor command. Reversal allows the carriage
to leave the obstacle. Zero friction and restitution isolate this path's
normal response.

## Read efforts after each step

The slider's vertical reaction carries the carriage weight. The hinge's
reaction carries both carriage and rail weights. At equilibrium, their
expected values are `mass * 9.81` and `(mass + 2) * 9.81` N respectively.
During acceleration and impact, include velocity changes and contact impulses
in the balance as well.

`world.write_contacts` exposes snapshots after `step`. The impulse applied to
the second body is `normal * normal_impulse + tangent_impulse`; the first
receives its opposite. The consumer orients the impulse towards the carriage
before checking `mass * velocity_change`. Slider and hinge reactions are
forces: multiply them by step duration to obtain impulses.

## Verified scope

Two masses, both sides of the pivot, 60/120 Hz, with and without the wall:
16 two-second recipes qualified against pinned Jolt in Native Debug/Release
on macOS ARM64. Motors respect their 2 N and 30 N·m capacities; contact must
actually appear with a significant impulse, then disappear. Linear and
carriage spin balances remain below 1e−5 N·s or N·m·s, geometry errors below
0.003 m or rad, and angle below 0.02 rad. Final speeds are below 0.005 m/s
or rad/s; final weight and torque errors below 0.05 N and N·m. Allowed
penetration is 0.003 m.

Silex measures contact impulses. The Jolt reference used here does not publish
their post-solve values: its normal component is inferred from motion and
slider reaction, without forming an independent normal balance. Its contact
state and vertical, rail and spin balances are checked separately. Contact
times, durations and transient efforts can differ between engines; no phase
or cost parity is claimed.

This recipe remains planar, without damping, sleep, friction or joint stops.
It does not qualify an arbitrary spatial chain. For a rail rotating freely
under a moving load without gravity, follow
[the rotation redistribution recipe](HingedRail3D.md).
