# Roll and resist sliding with passive tires

A tire gives a wheel rotational inertia and motion. Longitudinal contact spins
the wheel; lateral contact resists sideways drift. The world resolves reactions
through `world.step` alone. [Steering and brakes](VehicleControls3D.md)
are optional; this path shows rolling without controls. An [engine and transmission](VehiclePowertrain3D.md) can drive the wheels.

The [headless example](../../Examples/PassiveTires.sx) starts a 100 kg chassis
at 3 m/s with four stationary wheels. From the workspace root:

```sh
silex run Packages/GFX.Physics/Examples/PassiveTires.sx --release
```

Speed settles near 2.1429 m/s and each wheel rotates near 7.1429 rad/s. Part
of the chassis motion spins the wheels; their peripheral speed approaches
rolling speed. No engine launches them.

## Choose a tire

Configuration fragment to use in a wheel list:

```sx
Physics.Wheel3DSettings(
    Math.Vec3(-0.6, 0.0, -1.0),
    tire:Physics.Tire3DSettings(inertia:0.9, angular_damping:0.2)
)
```

`tire` defaults to `null`: [suspension alone](VehicleSuspension3D.md) retains
its behavior without tangential force or rotation. `Tire3DSettings` contains
rotational inertia in kg·m² (0.9), angular damping in s⁻¹ (0.2), local `forward`
(+Z) and `up` (+Y) directions, and two friction curves. Directions must be
finite unit nonparallel vectors; forward is projected perpendicular to up.
Inertia must be positive with a representable inverse, damping nonnegative;
both must be finite. Wheels remain virtual rotational degrees of freedom,
without additional rigid bodies or mass in the world.

## Tune grip

`TireFrictionCurve3D(points)` copies `Math.Vec2(slip, coefficient)` points.
At least one point is required. Abscissas must be nonnegative, strictly
increasing and finite; coefficients must be nonnegative and finite. The curve
interpolates linearly and clamps to endpoint values outside its range.
`coefficient(slip)` evaluates a finite nonnegative slip.

- `longitudinal_friction` uses the absolute ratio `abs(omega*r-v)/max(abs(v),0.001)`.
  Defaults: `(0,0)`, `(0.06,1.2)`, `(0.2,1)`.
- `lateral_friction` uses the acute angle between tangential velocity and
  the forward/backward axis, **in radians**, between 0 and π/2. Defaults: `(0,0)`, `(radians(3),1.2)`, `(radians(20),1)`.

Effective friction is the geometric mean of tire and **support** friction.
Chassis collider friction does not tune tire grip. Each tangential force is
bounded separately by this coefficient times normal force; this model does
not impose a combined friction circle. A zero-friction surface transmits no
tangential force.

## Read rotation and forces

The `vehicle.wheel(i)` snapshot adds to the suspension observations:

- `rotation_angle`, signed radians strictly between −2π and 2π;
- `angular_velocity`, signed rad/s, positive when rolling toward `forward`;
- `longitudinal_slip` and `lateral_slip`, ratio and radians;
- `longitudinal_direction` and `lateral_direction`, world contact axes;
- `longitudinal_force` and `lateral_force`, signed forces on the chassis in N.

Axes and slips are sampled at the start of the step, before constraint solving.
Rotation advances once after damping the step's initial wheel speed; final
speed and forces are read after solving. Forces are total step impulses
divided by step duration. The support receives the opposite reaction at the
same point. In flight, angles and speeds continue advancing, but contact slips,
axes and forces are zero. A zero step preserves observations; a disabled or
sleeping chassis preserves wheel rotation.

`vehicle.set_wheel_angular_velocity(i, value)` explicitly initializes a finite,
representable wheel speed and wakes the chassis. The wheel must have a tire
and the vehicle must be alive. This mutation is not a propulsion controller.
A wheel rotating above 10°/s delays chassis sleep. Removing support immediately
clears its forces; removing the chassis invalidates all wheel commands.

## Check behavior

The [public consumer](../../Tests/Consumer/Tests/VehicleTires3D.sx) checks
rolling, drift, a slippery surface, rotated frames, moving supports, balances,
sleep and lifetime. Two-body balances and wheel rotation balances are separate:
angular momentum conservation including virtual rotors is not claimed. Steep
friction curves can vary instantaneous slip values near pure rolling.

The qualification campaign uses Jolt’s actual wheeled controller with zero
engine torque and a neutral transmission: aligned/rotated rolling, lateral
drift, diagonal motion, damped free rotation and a moving jump. At 60/120 Hz
in Debug/Release on macOS ARM64, each engine produces 3072 observations and
52 corrupt-witness guards. Trajectories and rotations are compared at every
step, with independent impulse balances. Slips are recomputed within each
engine and compared through phase means; instantaneous equality near zero is
not claimed. Both worlds use 12 velocity and 4 position iterations, one worker
and no substeps; Silex retains its passes before and after integration. This
evidence does not yet qualify driving, execution speed or all terrain cases.
