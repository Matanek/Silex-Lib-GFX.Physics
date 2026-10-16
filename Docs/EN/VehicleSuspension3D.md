# Support a chassis with wheel suspensions

`WheeledVehicle3D` combines a dynamic chassis with suspended wheels. The world
finds supports by ray or swept sphere, solves springs and compression stops, and applies
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
| `contact` | `WheelContact3D.ray` by default; `WheelContact3D.sphere(radius)` for a volume contact |
| `minimum_length`, `maximum_length` | Suspension lengths in meters, `0.2` and `0.6`; these exclude the radius |
| `stiffness` | Per-wheel spring stiffness in N/m, `10000` |
| `damping` | Per-wheel damping in N·s/m, `1000` |
| `maximum_slope_angle` | Maximum angle between the support normal and opposite suspension direction, `pi/3` rad |

The spring’s natural length is `maximum_length`; it pushes when compressed
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
