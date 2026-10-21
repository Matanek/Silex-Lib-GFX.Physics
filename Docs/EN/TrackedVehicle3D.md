# Drive a vehicle with two tracks

`TrackedVehicle3D` combines a dynamic chassis with two tracks of suspended wheels.
The engine drives the tracks; their contacts transfer forces to the chassis and
supporting bodies. The world owns simulation stepping: the application calls
`world.step`, sends controls and reads state.

The [headless example](../../Examples/TrackedVehicle.sx) lands, accelerates and
brakes on a plane. From the workspace root:

```sh
silex run Packages/GFX.Physics/Examples/TrackedVehicle.sx --release
```

## Define the wheels and both tracks

Create wheels with `TrackedWheel3DSettings(position, ...)`, then two
`VehicleTrack3DSettings(driven_wheel, wheels, ...)`. Indices refer to the vehicle's
wheel array. Every wheel belongs to exactly one track; the driven wheel must
belong to that track. Both tracks are nonempty.

`TrackedVehicle3DSettings(chassis, wheels, left, right, ...)` retains the setup.
The wheel array and index arrays are copied. The chassis must be dynamic and
retains its rigid-body properties. The world creates only one body for the
vehicle; wheels do not add mass to the chassis.

| Wheel setting | Meaning and default |
| --- | --- |
| `position` | Local attachment in meters |
| `direction` | Unit local extension direction, `(0,-1,0)` |
| `radius` | Wheel radius, `0.3 m` |
| `minimum_length`, `maximum_length` | Suspension travel excluding radius, `0.2` and `0.6 m` |
| `stiffness`, `damping` | Spring `10000 N/m`, damper `1000 N·s/m` |
| `contact` | Ray search; sphere/cylinder searches are available through the shared foundation |
| `maximum_slope_angle` | Ray/sphere slope filter, `pi/3 rad` |
| `forward`, `up` | Local wheel axes, `(0,0,1)` and `(0,1,0)` |
| `longitudinal_friction`, `lateral_friction` | Constant coefficients, `4` and `2` |

Contact combines wheel and support coefficients through their geometric mean.
The [suspension and contact detection](VehicleSuspension3D.md) contracts apply.
An unsupported wheel applies no force to a support.

| Track setting | Meaning and default |
| --- | --- |
| `driven_wheel` | Driven wheel whose radius defines track speed |
| `wheels` | Distinct indices including the driven wheel |
| `inertia` | Track and wheel inertia seen at the driven wheel, `10 kg·m²` |
| `angular_damping` | Angular damping, `0.5 s⁻¹` |
| `maximum_brake_torque` | Maximum track brake torque, `15000 N·m` |
| `differential_ratio` | Gearbox to driven-wheel ratio, `6` |

Wheels on a track share linear belt speed. Their angular velocities can differ
when their radii differ: `omega_i = omega_driven * radius_driven / radius_i`.
Inertia belongs to the whole track. Required parameters and products must be
finite and representable; invalid topology is rejected before the chassis is
inserted into the world.

## Control driving

Create the vehicle with `world.create_tracked_vehicle(settings)`.
`set_controls(throttle, left_ratio, right_ratio, brake)` replaces persistent
controls; their defaults are `0, 1, 1, 0`.

| Control | Range and effect |
| --- | --- |
| `throttle` | `[-1,1]`; throttle magnitude and direction request for an automatic gearbox |
| `left_ratio`, `right_ratio` | `[-1,1]`, both nonzero; relative speeds and directions of the tracks |
| `brake` | `[0,1]`; fraction of each track's brake torque |

Keep both ratios at `1` to drive straight. Select
`left_ratio:0.5, right_ratio:1.0` to turn towards the vehicle's left; swap the
values for a right turn. `left_ratio:-1.0, right_ratio:1.0` requests opposing
track rotation to pivot. The result depends on grip, loads and available torque.
Zero ratios are rejected by this coupled model.

`set_controls()` releases throttle and brakes and restores both ratios to `1`.
`set_controls(brake:1.0)` brakes. Without tire grip, brakes stop the rotors but
cannot hold or stop the chassis on the ground.

[Engine and transmission settings](VehiclePowertrain3D.md) are shared. Track
vehicle defaults are a 500 N·m engine, 500 RPM idle and 4000 RPM maximum, with
forward ratios 4/3/2/1, reverse ratios −4/−3 and shift thresholds 1000/3500 RPM.
In manual mode, call `set_transmission(gear, clutch:1.0)`; negative gears select
reverse and 0 selects neutral. Track ratio signs remain a separate choice.

The controller uses an ideal coupling between tracks. With the engine connected,
its RPM follows the tracks subject to idle and maximum bounds; this differs
from the automotive implicit clutch: `clutch` scales transmitted torque, while
`clutch_strength` is not used by this controller. A zero idle engine with stationary tracks
does not start this coupled system. Automatic upshifts require support and
tracks rotating in the same direction. Brakes first slow track rotation, then
contacts transmit the remaining brake torque subject to grip limits.

## Observe, suspend and destroy

- `chassis()` returns the rigid body; `wheel_count()`, `wheel_settings(i)` and
  `wheel(i)` expose geometry, support, suspension length, angle, speed and forces.
- `track(VehicleTrackSide3D.left/right)` reports driven-wheel angular velocity,
  linear belt speed, applied drive torque and signed brake torque.
- `track_settings(side)` reads track settings; `powertrain()` reports RPM, gear,
  clutch and shift state. Read track drive/brake torque on `track`; wheels
  expose their contact forces.
- `set_track_angular_velocity(side, velocity)` initializes or changes the rotor
  in rad/s and wakes the chassis; wheel observations refresh on the next positive
  step. Wheel angles integrate the step's velocity before motor torque.

A zero step preserves observations. Disabling the chassis freezes tracks and
engine; enabling it resumes simulation. Unchanged controls do not wake it.
Throttle prevents sleep; wheel speed above 10°/s also keeps the chassis awake.
Wheels reported after a step reflect
their track's final speed, including unsupported wheels.

`world.destroy_tracked_vehicle(vehicle)` removes the chassis and suspensions.
Destroying `vehicle.chassis()` directly also invalidates the handle; destroying
a support clears its support references. World destruction invalidates its
handles. Check with `is_valid()`; other access to an expired vehicle is rejected.
Each vehicle remains attached to its original world.

`maximum_tilt_angle`, `up` and anti-roll bars use the shared foundation. The
qualification below enables neither bars nor tilt protection.

## Available qualification

Pinned Jolt 5.6.0 is compared against Silex Native Debug/Release on macOS ARM64.
Sixteen airborne cases cover ratios, unequal inertias and radii, transmission,
braking, input changes and engine speed limits. Six ground cases use a manual
gearbox and ray contacts on a plane: forward/reverse, opposite curves, pivot,
zero grip and recovery to
rest. Sphere/cylinder contacts remain available through the foundation; this
track campaign does not qualify them.

Comparisons retain per-step physical balances, chassis poses and velocities,
normal loads and resultant forces, with limits described in the
[qualification protocol](OracleAndBudgets.md). Tangential sharing among a track's
wheels does not define a unique individual force; no such parity is claimed.
This ideal track model does not simulate articulated links, continuous track
collision geometry or every terrain.
