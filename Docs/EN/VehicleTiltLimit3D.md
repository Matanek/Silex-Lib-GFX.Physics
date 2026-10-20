# Limit a vehicle’s pitch and roll

`maximum_tilt_angle` sets the total allowed inclination between the chassis up
direction and the vertical opposite to gravity. This stability aid forms a cone:
one angle bounds combined pitch and roll while yaw remains free. The default
`Math.pi()` leaves the vehicle unconstrained.

The [headless example](../../Examples/VehicleTiltLimit.sx) starts at 60° in flight
and compares a free vehicle with a 30° cone:

```sh
silex run Packages/GFX.Physics/Examples/VehicleTiltLimit.sx --release
```

After one second at 120 Hz it prints approximately 60° and 30°. To configure
a vehicle with chassis settings and wheels already constructed:

```sx
Physics.WheeledVehicle3DSettings(chassis, wheels,
    maximum_tilt_angle:Math.pi()/6.0,
    up:Math.Vec3.up())
```

`up` is a unit axis in the chassis local frame. The world vertical follows world
gravity; zero gravity retains the last vertical. Before the first step with
nonzero gravity, that vertical is initialized from `up`. Changing local up
requires recreating the vehicle.

## Change the limit during simulation

`vehicle.maximum_tilt_angle()` reads the limit in radians.
`vehicle.set_maximum_tilt_angle(angle)` replaces it and wakes the chassis.
The next positive step handles the new limit; `world.step(0.0)` preserves pose
and observations. Each instance owns its limit. Reading or changing it after
vehicle destruction produces a diagnostic.

The angle must be finite within `[0, pi]`, and `up` must be finite and unit length.
The getter reconstructs the angle from its cosine and may differ from the
original setting by rounding, especially near zero. Anti-roll bars and suspensions remain independently
configured.

## Understand the correction

The limit applies a unilateral angular impulse to the chassis outside the cone,
then gradually corrects its pose during position passes. It also acts without
wheel support. The world owns this work: applications keep calling only
`world.step`. This stability aid does not correct translation.

An initial pose outside the cone gradually returns toward the boundary. A zero
angle is accepted but recovery becomes slow near the vertical. Position iteration
count affects recovery; an instantaneous orientation bound after impact is not
guaranteed.

Exactly opposite to the vertical, the correction axis is indeterminate. As in
Jolt, the vehicle reuses its previous axis; a freshly created, exactly inverted
instance may therefore remain inverted. A slightly inclined initial pose or
initial motion defines a physical recovery direction. This aid is not a
motorcycle balance controller.

## Evidence and scope

The [public consumer](../../Tests/Consumer/Tests/VehicleTiltLimit3D.sx) exercises
opposite and diagonal axes, flight, translation, yaw, changed limits, rotated then
zero gravity, distinct local up, zero steps, sleeping and destruction.
`VehicleTiltLimitRun.py` compares these situations with the pinned Jolt
`VehicleConstraint` at 60/120 Hz in Native Debug/Release on macOS ARM64.
Free-flight balances are checked independently of engine comparisons.

The supported case starts level with a .0025 rad limit (about .14°) to isolate
the angular row under a 40 N·m load with anti-roll bars, followed by a jump and
regained support. Stop impacts after strong loading and large free
toppling remain outside this bounded qualification. See
[anti-roll bars](VehicleAntiRoll3D.md) and [suspensions](VehicleSuspension3D.md).
