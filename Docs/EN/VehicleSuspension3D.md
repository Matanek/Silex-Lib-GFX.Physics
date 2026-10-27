# Support a chassis with wheel suspensions

`WheeledVehicle3D` combines a dynamic chassis with suspended wheels. The world
finds supports by ray, swept sphere or cylinder, solves springs and compression stops, and applies
reactions to both bodies. The application only calls `world.step`. Without an optional tire, wheels only apply suspension.
[Passive tires](PassiveTires3D.md) add rolling and grip; [controls](VehicleControls3D.md)
add steering and braking. The [powertrain](VehiclePowertrain3D.md) adds propulsion.

The [complete headless example](../../Examples/VehicleSuspension.sx) supports
100 kg on four suspensions. From the workspace root:

```sh
silex run Packages/GFX.Physics/Examples/VehicleSuspension.sx --release
```

It prints a height near 0.8755 m. Each spring supports approximately 245.25 N;
together they balance the 981 N weight.

## Define wheels and chassis

`WheeledVehicle3DSettings(chassis, wheels)` takes settings for a **dynamic**
body and at least one `Wheel3DSettings`. The wheel array is copied. The chassis
retains ordinary shape, mass, center of mass, inertia, collision and sleep
settings. Wheels create no additional rigid bodies and add no chassis mass.

| Wheel setting | Meaning and default |
|---|---|
| `position` | Attachment in meters, relative to the chassis shape origin |
| `direction` | Unit local extension direction, `(0,-1,0)` |
| `radius` | Wheel radius in meters, `0.3` |
| `contact` | `WheelContact3D.ray` by default; `WheelContact3D.sphere(radius)` or `WheelContact3D.cylinder(width)` for volume contact |
| `minimum_length`, `maximum_length` | Suspension lengths in meters, `0.2` and `0.6`; these exclude the radius |
| `stiffness` | Per-wheel spring stiffness in N/m, `10000` |
| `damping` | Per-wheel damping in N·s/m, `1000` |
| `preload_length` | Preload in meters, `0`; travel unchanged |
| `spring` | Frequency/ratio or mass-normalized coefficients; `null` keeps SI coefficients |
| `force_point` | Optional local force point; `null` uses the actual contact |
| `maximum_slope_angle` | Maximum angle between the support normal and opposite suspension direction, `pi/3` rad |

The spring’s natural length is `maximum_length + preload_length`; it pushes when compressed
and never pulls the support. `minimum_length` is a rigid compression stop.
Equal lengths remove spring travel and retain that stop. Parameters must be
finite: positive radius and stiffness, nonnegative damping and lengths, with a
strictly positive maximum at least equal to the minimum. The angle lies in
`[0,pi/2)`.

The support ray starts at the attachment and spans `maximum_length + radius`.
Observed length is the support distance minus the radius, clamped to zero.
The chassis is ignored; sensors and collision-filtered pairs are excluded.
The nearest surface whose normal satisfies the maximum angle becomes the
support. Static, kinematic and dynamic bodies can support suspension; a dynamic
support receives the opposite reaction at the same contact point. A ray does
not reproduce tire width on a narrow edge.

## Set preload and spring response

`preload_length` adds a preload in meters, zero by default. The natural length
becomes `maximum_length + preload_length`; search travel and both stops remain
unchanged. A 1 cm preload therefore raises equilibrium by 1 cm while the wheels
retain support without reaching a stop.

The optional `spring` parameter sets response without choosing physical
coefficients that depend on mass. Wheel construction fragment:

```sx
Physics.Wheel3DSettings(Math.Vec3(), preload_length:0.01,
    spring:Physics.SuspensionSpring3D.frequency(3.0,0.8))
```

- `frequency(hertz, ratio)` selects a strictly positive frequency and a
  nonnegative damping ratio; `1` means critical damping.
- `mass_normalized(stiffness, damping)` selects coefficients in s⁻² and s⁻¹.
  The first is strictly positive and the second nonnegative.

The calculation accounts for chassis mass and inertia, the arm around its
center of mass and the vehicle's local up axis. Support mass does not enter
this conversion. With identical geometry and inertia distribution, doubling
mass preserves frequency and static sag. Without `spring`, `stiffness` and
`damping` retain their SI units and behavior. Combining an alternative mode
with nondefault SI coefficients is rejected; leave those two arguments at
their defaults. Values and their conversions must remain finite and representable.

`force_point:Math.Vec3(...)` selects the local chassis point where suspension
and tire forces act. Without it, forces act at the actual contact. A point near
the center of mass reduces the force's roll moment; a point exactly at the
center removes that moment. The opposite reaction on a dynamic support acts
at the same world point, preserving the pair's balance. The `contact_point`
and `contact_normal` snapshots still describe the actual collision. Choosing
this point tunes vehicle behavior without changing its geometry.

These settings also belong to `TrackedWheel3DSettings`; both `Motorcycle3D`
wheels use `Wheel3DSettings` directly. The
[settings consumer](../../Tests/Consumer/Tests/VehicleSuspensionSettings3D.sx)
checks inheritance, equilibria, angular response and momentum conservation
on a dynamic support. `VehicleSuspensionSettingsRun.py` compares nine 6 s
recipes at 60/120 Hz with original Jolt and the center of mass at the origin,
Native Debug/Release on macOS ARM64:
preload, doubled mass, spring modes, roll, jump and overload. This proof does
not qualify every possible setting.

## Reach an edge with a sphere

The [ray/sphere example](../../Examples/VehicleSphereContact.sx) places an anchor
20 cm beyond an edge. Its center ray misses the support; a swept 30 cm sphere
finds it. From the workspace root:

```sh
silex run Packages/GFX.Physics/Examples/VehicleSphereContact.sx --release
```

The program prints `support=false` for the ray and `support=true` for the
sphere, with approximately `0.5263932` m of suspension. Choose the contact
in each wheel's settings. Fragment to use when creating a wheel:

```sx
Physics.Wheel3DSettings(Math.Vec3(), contact:Physics.WheelContact3D.sphere(0.3))
```

The cast sphere radius is separate from `radius`, which serves rolling,
brakes and propulsion. The sphere starts at the anchor and travels
`maximum_length + radius - sphere_radius`. Observed length equals hit fraction
times that travel, plus `sphere_radius - radius`, clamped at zero. The sphere
radius must be positive and less than `maximum_length + radius`;
unrepresentable scales are rejected.

The point and normal describe the support surface. Filters, sensors and maximum
slope are applied before selection, including between compound or mesh leaves.
The nearest admissible support is retained; if several surfaces initially overlap
the sphere, the deepest penetration is retained. The world then applies the same
springs, reactions, tires and controls. A sphere approximates contact volume;
it does not reproduce tire width or its cylindrical shape.

## Include tire width in contacts

The [width example](../../Examples/VehicleCylinderContact.sx) compares two
wheels whose anchor extends 15 cm beyond an edge. A 10 cm width misses the
support; a 40 cm width supports the wheel with 0.45 m suspension length:

```sh
silex run Packages/GFX.Physics/Examples/VehicleCylinderContact.sx --release
```

Choose `contact:Physics.WheelContact3D.cylinder(0.4)` when creating a wheel
with a total width of 40 cm. The cylinder uses `Wheel3DSettings.radius`, starts
at the anchor and travels `maximum_length` along the suspension direction.
The observed length is the hit fraction multiplied by that travel.
Its axle follows the chassis, current steering and the optional tire’s
`forward`/`up` directions; without a tire these are `(0,0,1)` and `(0,1,0)`.
Rolling rotation leaves this volume of revolution unchanged.

The cylinder has sharp, unrounded rims. Width, radius and travel must be
positive and representable; scales whose square becomes zero or non-finite
are rejected. This mode ignores `maximum_slope_angle`, like Jolt’s cylinder
tester: a wall or rim may therefore provide a contact. Bilateral filters,
sensors, disabled bodies and chassis exclusion still apply. The earliest
contact, or deepest initial penetration, becomes the support, including
among compound/mesh leaves.

A cylindrical tread can touch a face along a line. When the axle is tangent
to the contact plane, the world prefers the wheel center’s projection if it
belongs to both boundaries; otherwise it retains the point found on the
support. Suspension and tires always react at that physical point. Different
valid points on this line can produce different instantaneous impact moments.

The [cylinder consumer](../../Tests/Consumer/Tests/VehicleCylinderContact3D.sx)
covers width, first-step steering, camber, filters, pause, overlap and dynamic
support reaction. `VehicleCylinderContactsRun.py` compares 21 configurations
and two dynamic recipes at 60/120 Hz in Native Debug/Release on macOS ARM64:
geometry, trajectory, rest/weight and per-step balances. Angular velocity uses
quarter-second means; instantaneous landing parity is not claimed. Line-contact
points are qualified by boundary membership, without arbitrary coordinate equality.

Jolt’s corner normal differs from the analytic radial normal by about 0.011;
only this equality is excluded, while boundaries and length remain checked.
Silex retains the analytic normal. The Jolt rotated infinite-plane point limit
described below is separate; a tilted box carrying that plane qualifies the
physical point. These recipes qualify neither every driving scene nor
performance parity.

## Read supports and trigger a reaction

`world.create_wheeled_vehicle(settings)` creates the vehicle.
`vehicle.chassis()` provides its rigid body handle: apply forces and impulses
through the ordinary body commands. `wheel_count()` returns the number of wheels
and `wheel_settings(i)` reads their copied settings.

`vehicle.wheel(i)` returns an independent `VehicleWheelState3D` containing:

- `length`, observed suspension length in meters;
- `normal_force`, normal force solved during the last positive step, in N;
- `support()`, the optional support body handle;
- `contact_point` and `contact_normal`, the world support point and normal.

Length and contact are evaluated at the start of the step; the chassis pose is
read after integration. Force is the total impulse solved during that step
divided by its duration. It varies with acceleration at a stop or during an
impact. An unsupported wheel has maximum length, zero force and zero point/normal.
A disabled or sleeping vehicle solves no new force. A zero step preserves the
last observation.

## Ownership and sleep

`world.destroy_wheeled_vehicle(vehicle)` removes the chassis and invalidates
the vehicle. Removing its chassis directly has the same effect. The world
checks ownership; stale handles and out-of-range wheel indices produce a
diagnostic. Previously read values remain snapshots, whose optional support
handles can subsequently become invalid.

Supports participate in sleep and wake islands. A moving kinematic support
wakes the chassis; destroying its support clears contact and wakes it to resume
falling. Multiple vehicles can share settings without sharing suspension state.

## Evidence and scope

The [public consumer](../../Tests/Consumer/Tests/VehicleSuspension3D.sx) checks
weight, loaded stops, jumping, moving supports, momentum balances, offset mass
centers, filters, sleep and lifetime. The public `VehicleSuspension` witness
compares four suspensions with Jolt’s real `VehicleConstraint` at 60/120 Hz,
Native Debug/Release on macOS ARM64, using 12 velocity and 4 position iterations
in both engines. Soft suspension uses trajectory comparisons; loaded stops use
geometry, discrete balances and phase mean reactions over fixed windows.
General instantaneous impact reaction parity and performance parity are not
claimed.

The [sphere consumer](../../Tests/Consumer/Tests/VehicleSphereContact3D.sx)
checks edges, reach, slope rejection, initial contact, filters, disabling,
creation/destruction and momentum conservation with a dynamic support.
`VehicleSphereContactsRun.py` compares 19 geometric configurations and four
dynamic recipes against Jolt at 60/120 Hz in Debug/Release. Soft suspension on
a flat floor and gripped edge trajectories are compared; actual public normal
and lateral force readings close each engine's impulse balances. Hard loading
retains qualification through geometry and phase mean forces.

Without grip, symmetric support on two edges is unstable: a 1e-6 m initial
Jolt offset is enough to tip the chassis. Trajectory comparison for that recipe
ends at 1.5 s; balances retain every sample. The pinned Jolt tester also returns
an off-surface point on a rotated infinite plane: only length and normal are
compared there. A tilted box carrying the same plane qualifies the physical
point. Silex keeps its support point; no equality with that incorrect Jolt
point is claimed.

[Reduce body roll with paired suspension bars](VehicleAntiRoll3D.md).
