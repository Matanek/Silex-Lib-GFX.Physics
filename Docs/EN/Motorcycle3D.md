# Balance and steer a motorcycle

`World3D.create_motorcycle` combines a dynamic chassis, a front wheel and a rear
wheel with balance assistance. Contacts, suspensions and tires remain physical;
the world applies the assist torques during its step. Disabling assistance lets
the motorcycle fall.

The [headless example](../../Examples/Motorcycle.sx) starts at 0.2 rad roll,
returns upright on both supports, then destroys the motorcycle. From the
workspace or Spec group root:

```sh
silex run Packages/GFX.Physics/Examples/Motorcycle.sx
```

Both wheels also accept [preload, spring modes and a local force point](VehicleSuspension3D.md#set-preload-and-spring-response).

## Describe the chassis and both wheels

`Motorcycle3DSettings(chassis, front, rear)` reuses `RigidBody3DSettings` and
`Wheel3DSettings`. Each wheel requires `Tire3DSettings`. Wheel positions and
suspension directions are local to the chassis. In observations, `wheel(0)`
is the front and `wheel(1)` is the rear.

The wheelbase is the front-to-rear distance projected onto `forward`, measured
at the fully extended suspension endpoints; it must be positive. `up` defaults
to Y and `forward` to Z. Both directions must be unit and orthogonal. Settings
retain their own wheel and chassis values; changing their source after creation
does not reconfigure a motorcycle.

The engine is optional. The `engine` parameter adds the
[engine and transmission](VehiclePowertrain3D.md) shared with wheeled vehicles;
`drive_ratio`, defaulting to 3.42, drives the rear wheel. Without an engine,
nonzero `throttle` and reading the powertrain are rejected.
`set_controls(steering, brake, handbrake, throttle)` and `set_transmission`
retain the [wheel control conventions](VehicleControls3D.md).

## Tune assistance

`MotorcycleBalance3DSettings` describes the actuator's target and gains:

| Setting | Meaning | Default |
| --- | --- | --- |
| `maximum_lean_angle` | Maximum target lean, in `[0, pi/2)` | `pi/4` rad |
| `stiffness` | Proportional torque, in N·m/rad | `5000` |
| `damping` | Damping, in N·m·s/rad | `1000` |
| `integral_gain` | Integrated error gain, in N·m/(rad·s) | `0` |
| `integral_decay` | Integral decay without support | `4` s⁻¹ |
| `smoothing` | Previous target weight, in `[0, 1]` | `0.8` |

Gains and decay must be nonnegative, finite and representable. `smoothing=0`
follows observed forces directly; `smoothing=1` retains the previous direction
after initialization. Smoothing runs per step. Decay multiplies the integral
by `max(0, 1-integral_decay*dt)` on each solver call without loaded supports,
so its effect also depends on iterations. The default `integral_gain=0` does
not use the integral.

Fragment, on an existing motorcycle:

```sx
bike.set_balance_settings(Physics.MotorcycleBalance3DSettings(
    stiffness:3000.0, damping:700.0, maximum_lean_angle:0.5))
bike.set_balance_enabled(false)
bike.set_balance_enabled(true)
```

Changing settings retains the integral; disabling assistance resets it on the
next active step. These mutations wake the chassis.

## Lean, steering and supports

The target follows the previous step's normal and lateral force resultant,
projected perpendicular to the motorcycle's forward direction, then clamped by
`maximum_lean_angle`. `lean_target()` returns that world direction; it returns
the zero vector before the first positive step.

Assistance applies torque around the forward axis only when both wheels have
loaded contacts. A chassis velocity correction compensates the mean contact
velocity change. This is an external actuator: no opposite torque is applied
to supports. Without support, assistance does not right the motorcycle in flight.

Steering is limited according to wheelbase, squared forward speed, gravity and
each wheel's caster. `set_steering_limit_enabled(false)` removes this limit
without disabling balance. Both switches are independent and enabled by default.
The limit bounds steering amplitude: reversing the maximum wheel angle or its
axis preserves the signed wheel convention.
`maximum_tilt_angle`, distinct from the assistance target, remains an optional
[tilt cone](VehicleTiltLimit3D.md) defaulting to `pi`.

The [wheel slope filter](VehicleSuspension3D.md) remains relative to the
suspension direction. Its `pi/3` default may release a support as the motorcycle
falls. On the comparison plane, the witness explicitly uses `pi/2-1e-6` to
compare the same geometric contacts with Jolt's world-vertical tester.

## Ownership and qualification

The world owns the chassis and simulation. `destroy_motorcycle`, destruction
of its chassis or the end of the world's lifetime invalidate all its handles;
`is_valid()` remains available. A foreign world cannot destroy the motorcycle.
Settings are validated before insertion. `step(0)` computes neither a pose nor
a new target; controls and configuration mutations are forbidden during a step.

The initial balance comparison covers 16 recipes at 60/120 Hz, with Native
Debug/Release on macOS ARM64: balance, disabling/re-enabling, jumping, coasting turns, smoothing,
target limits and airborne steering. The engine has zero torque in these
recipes. Both modes produce identical outputs. Once the falling, unassisted
chassis center drops below 0.2 m, the proof checks the event and bounded state,
without pointwise rebound angle parity.

Composed driving on a plane is now qualified with ray/sphere contacts, and all
three detectors have a terrain campaign with propulsion disabled. Wide cylinders
retain repose and trajectory-parity limits: see the
[current profiles](VehicleQualification3D.md) and
[witnesses and budgets](OracleAndBudgets.md).
