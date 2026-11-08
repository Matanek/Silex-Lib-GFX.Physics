# Power a wheeled vehicle

An engine and transmission drive the powered wheel rotors. Tire contacts then
transfer force to the chassis. The [complete example](../../Examples/VehiclePowertrain.sx)
accelerates, turns and stops with an automatic gearbox:

```sh
silex run Packages/GFX.Physics/Examples/VehiclePowertrain.sx --release
```

## Choose the engine and driven wheels

Fragment with an existing chassis and a list of tire-equipped wheels:

```sx
var settings=Physics.WheeledVehicle3DSettings(chassis,wheels,
    engine:Physics.VehicleEngine3DSettings(maximum_torque:30.0),
    differentials:[Physics.VehicleDifferential3DSettings(0,2)])
var vehicle=world.create_wheeled_vehicle(settings)
vehicle.set_controls(throttle:0.5)
world.step(1.0/120.0)
```

Differential indices identify wheels 0 and 2 here; their front/rear meaning
depends on your list. Each driven wheel needs a tire and belongs to one
differential. An index of −1 means that side is absent:
`VehicleDifferential3DSettings(0)` drives wheel 0 alone. All
`engine_torque_ratio` shares must total 1; for example, use 0.5 per axle for
all-wheel drive. Other wheels remain free.

Without `engine`, the vehicle retains passive rolling behavior. Adding an
engine requires at least one differential. Engine settings, ratios and the
differential list are copied during construction; modifying the original
arrays does not reconfigure an existing vehicle.

## Accelerate, steer and brake

`set_controls(steering:0,brake:0,handbrake:0,throttle:0)` replaces the complete
persistent command. Omitted inputs return to zero. Throttle must be finite in
[−1,1]: its absolute value controls engine torque; its sign selects the desired
direction for an automatic gearbox. In manual mode, the selected gear sets the
direction. [Steering and brakes](VehicleControls3D.md) combine with the engine.

A changed command wakes the chassis; repeating it does not. The world advances
the engine only on positive active chassis steps. A zero step preserves
observations; disabling the chassis also freezes its RPM and wheel rotation.
Destroying the chassis invalidates commands and reads. Nonzero throttle, RPM
above idle or a transmission transition prevents sleep; zero input can allow it.

## Tune the engine

`VehicleEngine3DSettings` uses N·m, RPM, kg·m² and seconds:

| Parameter | Default | Effect |
|---|---:|---|
| `maximum_torque` | 500 | Nonnegative maximum engine torque |
| `minimum_rpm` / `maximum_rpm` | 1000 / 6000 | Enforced idle and governed maximum RPM |
| `inertia` | 0.5 | Strictly positive engine rotor inertia |
| `angular_damping` | 0.2 | RPM damping |
| `torque_curve` | (0,0.8), (0.66,1), (1,0.8) | Torque fraction versus RPM/maximum RPM |

The curve interpolates linearly and clamps to endpoint values. Its abscissas
must strictly increase, with all coordinates finite and in [0,1]; at least one
point is required. Its abscissa is **RPM/maximum_rpm**, including at idle.
`engine.torque(rpm,throttle:...)` evaluates torque for finite nonnegative RPM
and throttle in [0,1].

Damping multiplies RPM by `max(0,1-angular_damping*dt)`, then clamps it. The
clutch subsequently couples the engine to the wheels. RPM bounds are enforced
as in Jolt; idle can supply energy. They do not model engine stalling or global
energy conservation.

## Choose a transmission

The default automatic gearbox chooses direction from throttle, then shifts
according to RPM. It does not shift up while a driven wheel lacks support,
its longitudinal slip exceeds 0.1, or RPM is decreasing. The clutch opens during
a shift, then engages progressively.

To select gears yourself, configure manual mode when creating the vehicle.
Fragment for a vehicle configured in manual mode:

```sx
vehicle.set_transmission(1)             // first gear, clutch engaged
vehicle.set_transmission(0)             // neutral
vehicle.set_transmission(-1,clutch:0.5)  // reverse, partial clutch
```

`VehicleTransmission3DSettings(mode:VehicleTransmissionMode3D.manual)` retains
initial neutral until a call. `clutch` must be finite in [0,1]: 0 disengages it,
1 engages it. Positive gears index forward ratios; negative gears index reverse
ratios. `gear_ratio(gear)` and the gear count methods inspect a configuration.
The main parameters are:

| Parameter | Default |
|---|---|
| `gear_ratios` | [2.66, 1.78, 1.3, 1, 0.74], all strictly positive |
| `reverse_gear_ratios` | [−2.9], all strictly negative |
| `clutch_strength` | 10 kg·m²/s, nonnegative |
| `clutch_torque_limit` | `null`; finite nonnegative engine-side torque limit in N·m |
| `switch_time` / `clutch_release_time` / `switch_latency` | 0.5 / 0.3 / 0.5 s |
| `shift_up_rpm` / `shift_down_rpm` | 4000 / 2000 RPM |

Times must be nonnegative, thresholds ordered and lists nonempty.
`set_transmission` requires manual mode. Invalid or unrepresentable inputs
panic, including throttle on a vehicle without an engine.

`clutch_torque_limit` bounds actual transmitted clutch torque in both drive and
braking, before gearbox and differential ratios. Its capacity is multiplied by
current engagement and the `clutch` input to `WheelDrive3D.step`. The solver uses
the same bounded torque for engine and wheels, preserving their angular momentum
balance. `null` preserves the previous coupling without an explicit limit; `0`
prevents torque transfer. This setting applies to `WheeledVehicle3D` and
`WheelDrive3D`, which own this clutch. Tracked vehicles retain their separately
documented direct coupling.
The [consumer test](../../Tests/Consumer/Smokes/WheelDriveClutchLimit3D.sx) checks
saturation in both directions, pressure and angular momentum balance at 60,
120 and 960 Hz.

## Distribute torque and observe the result

Each `VehicleDifferential3DSettings` has a positive ratio (default 3.42), a
`left_right_split` (0.5 splits equally) and an `engine_torque_ratio` share
(default 1). `limited_slip_ratio` defaults to 1.4; `null` gives an open
differential. A finite limit greater than 1 redirects torque towards the slower
side under propulsion, and towards the faster side when torque opposes
rotation, including engine braking and a direction reversal. Wheels still
spinning the opposite way remain distinct from those already driven in the
new direction. Redistribution therefore reduces the speed difference in
either case. Vehicle settings also provide
`differential_limited_slip_ratio` (default 1.4, or `null`) to distribute torque
between axles using the same principle.

Split and engine shares are nominal: limited slip can change them. Remove a
differential to disconnect its wheels; a zero share does not disconnect them
while limited-slip redistribution is active.

`vehicle.powertrain()` returns a read-only snapshot: `engine_rpm`, `gear`,
`clutch`, `switching_gear` and `engine_torque` in N·m. The observed gearbox has
already advanced for the next step; torque belongs to the completed step.
`vehicle.wheel(i).drive_torque` is the signed engine torque delivered to that
rotor, separate from braking and damping. In flight, rotors accelerate but the
chassis receives no propulsion force. In neutral or with an open clutch, the
engine can rev without driving the wheels.

Coupling and controls are qualified against the actual Jolt controller at
60/120 Hz on macOS ARM64 in Debug/Release. Public consumers add analytic
solutions, body reactions, copies and lifetime checks. Near a stop, primary states and formulas remain checked;
contact velocities are compared through phase means. Instantaneous parity of
contact velocity or ill-conditioned angles is not claimed. Other wheel detectors, anti-roll bars, tracked vehicles and
motorcycle balance remain separate capabilities.

## Drive your own rigid wheels

`WheelDrive3D` uses the same engine, clutch and gearbox when rims and tires are
simulated separately, for example with soft tires. The
[executable consumer](../../Tests/Consumer/Smokes/WheelDrive3D.sx) checks coupling
to external rotors. Fragment for four wheels already being simulated:

```sx
var drive=Physics.WheelDrive3D(
    Physics.VehicleEngine3DSettings(maximum_torque:145.0),
    Physics.VehicleTransmission3DSettings(gear_ratios:[3.2,2.3,1.6]),
    wheel_inertias:[16.0,16.0,16.0,16.0],
    differentials:[Physics.VehicleDifferential3DSettings(0,2,engine_torque_ratio:0.5),
        Physics.VehicleDifferential3DSettings(1,3,engine_torque_ratio:0.5)],
    differential_limited_slip_ratio:1.4)
```

Each substep, call `set_wheel(index,angular_velocity,grounded:...,slipping:...)`
for every wheel, then `step(delta,throttle,torque_scale:1,clutch:1)`. Supply
angular velocity **relative to the chassis**, in rad/s, using the same positive
sense for all wheels. Inertias are the effective inertias around that axis, in
kg·m², including parts rotating with the rim. Differential indices and shares
follow the rules above. Arrays are retained independently of later caller edits.

Apply `wheel_torque(index)` in N·m to each wheel and its opposite reaction to
the chassis, then advance the world by the same `delta`. This controller does
not advance bodies itself. Read actual post-contact speeds for the next step;
do not apply another velocity correction or the raw engine torque. Brakes
belong to the wheel assembly. `grounded` and `slipping` inform upshift protection
without creating contact forces.

The step must be finite in [0,1] seconds; a zero step preserves state and torques.
`torque_scale` is finite and nonnegative; it multiplies combustion torque, for
example for a boost. `clutch`, finite in [0,1], multiplies the gearbox clutch,
allowing progressive launch or disengagement during braking. Otherwise, the
imposed idle can push stationary wheels. In manual mode,
`set_transmission(gear,clutch:...)` retains its role; the pressure supplied to
`step` multiplies that command. Invalid inputs panic.


`differential_limited_slip_ratio` also controls redistribution between your
axles. Its `null` default retains nominal shares; a finite value above 1, such
as 1.4, sends more torque to the slower axle as speeds diverge. This is separate
from each differential’s left/right limited slip. It can supply loaded wheels
when another axle spins.

`state()` returns `VehiclePowertrainState3D`: RPM, gear, effective clutch,
transition and engine torque. These observations can drive a dashboard or a
sound engine. GFX.Physics has no audio library dependency.
