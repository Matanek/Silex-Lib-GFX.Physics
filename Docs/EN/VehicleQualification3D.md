# Qualified 3D vehicle profiles

Cars, tracked vehicles and motorcycles use the same rigid-body world. The world
advances suspension, contacts, tires and transmission on each step; controls
remain active until replaced. These models work without rendering and feed the
existing `Silex-Examples` scenes.

| Vehicle | Model and settings | Observed driving profiles |
| --- | --- | --- |
| Car | [Suspended wheels](VehicleSuspension3D.md), [tires and brakes](VehicleControls3D.md), [engine and gearbox](VehiclePowertrain3D.md) | Starting, mirrored turns, braking, reverse, incline, jumping and regaining support |
| Tracked vehicle | [Two ideal bands](TrackedVehicle3D.md), shared engine and gearbox | Turning through relative speeds, pivoting, braking, automatic gears, ramp, moving supports and prolonged driving |
| Motorcycle | [Two wheels and adjustable assistance](Motorcycle3D.md), rear-wheel drive | Balance, speed-dependent steering limit, optional assistance, acceleration/braking, ramp, flight and landing |

The shared suspension accepts SI coefficients, frequency with damping ratio or
mass-normalized coefficients, preload and an optional local force application
point. Cars can also use [anti-roll bars](VehicleAntiRoll3D.md) and a
[tilt limit](VehicleTiltLimit3D.md). Contact forces transmit propulsion and apply
reactions to a dynamic support.

## Choosing contacts and the time step

Ray contacts are the default. Spheres reach around edges; cylinders represent
wheel width and orientation. All three families have contact witnesses on a
horizontal/inclined box, edge, two-triangle mesh, height grid and free support of
finite mass. These scenarios isolate suspension by disabling propulsion and
tangential grip.

Composed driving on a fixed plane is qualified at 60/120 Hz, 12 velocity and
4 position iterations, with one worker and no additional substeps. Ray/sphere
profiles combine acceleration, opposite turns, actual ground friction set to
zero and restored, braking, reverse and stopping. Cars and motorcycles use
variable tire curves; tracked vehicles retain ideal bands. Momentum balances
include the motorcycle assistance's linear compensation.

Prolonged tracked driving has a separate profile with 48/4 iterations. The
12/4 profile remains outside the straightness budget on that route; additional
iterations belong to the qualified configuration and do not change the world's
defaults. These witnesses establish no guarantee for every combination of
settings or terrain.

## Wide-cylinder limits

A rigid cylinder contacting a plane can form a line. The numerical point chosen
on that line affects torque. During composed driving, Jolt itself exceeds the
trajectory budgets under a common 0.1 mm translation of the vehicle and ground,
or under mirrored controls. Full parity of these cylinder trajectories remains
unqualified; geometry, grip and impulse checks remain active.

The motorcycle with 0.4 m wide cylinders also retains low-speed oscillation in
both engines: speed can still reach 0.28 m/s at the measured stops. This profile
does not establish repose below 0.05 m/s. Use ray or sphere contacts for the
motorcycle driving profile qualified through stopping. Cylinder geometry alone
does not supply a deformable tire model.

## Ownership and observations

Each vehicle has one chassis registered in its world. Destroying the facade,
its chassis or the world invalidates existing handles; a new instance never
reactivates old handles. `is_valid()` checks their state. Destroying a support
removes it from subsequent observations. A previously read snapshot retains its
values and support handle, which becomes invalid: check `is_valid()` before
reusing that handle.

Changing vehicle controls or settings wakes the affected instance. A disabled
body retains its pose and observations; `step(0)` does not recompute physics.
Public tests mix all three families and several orders of destruction and slot
reuse: [mixed consumer](../../Tests/Consumer/Tests/VehicleFleet3D.sx).

Measurements execute with Native Debug/Release on macOS ARM64. They do not
measure FPS, qualify multiple workers or establish execution on other platforms.
Scenarios, reference variants and budgets are detailed in the
[comparison evidence](OracleAndBudgets.md).
