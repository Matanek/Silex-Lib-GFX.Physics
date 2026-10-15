# Steer and brake a vehicle

Tire-equipped wheels can steer and brake their rotation. Contact transfers
forces to the chassis and support; the world retains simulation stepping.
The [complete headless example](../../Examples/VehicleControls.sx) launches a
vehicle at 3 m/s, turns it, then stops it:

```sh
silex run Packages/GFX.Physics/Examples/VehicleControls.sx --release
```

## Choose which wheels steer and brake

Configuration fragment for the wheel list of a `WheeledVehicle3DSettings`:

```sx
Physics.Wheel3DSettings(
    Math.Vec3(-0.6, 0.0, 1.0),
    tire:Physics.Tire3DSettings(),
    maximum_steering_angle:Math.radians(30.0),
    maximum_brake_torque:1500.0,
    maximum_handbrake_torque:0.0
)
```

`maximum_steering_angle` defaults to 0: that wheel does not steer. A signed
value between −π/2 and π/2 sets its amplitude; a negative value enables
counter steering. `steering_axis` is a finite unit local axis, default +Y.
Steering rotates the tire frame about this axis, without moving the anchor
or changing the suspension direction.

Maximum service and handbrake torques must be nonnegative, finite and
representable relative to the radius, in N·m. Defaults are 1500 and 0. Configure
handbraking only on the intended wheels, such as the rear pair. Without a tire,
steering remains observable but no tangential force or brake torque acts.
See [passive tires](PassiveTires3D.md).

## Set persistent controls

Fragment with an existing vehicle:

```sx
vehicle.set_controls(steering:0.4)
world.step(1.0/120.0)
vehicle.set_controls(brake:1.0)
world.step(1.0/120.0)
vehicle.set_controls()
```

`set_controls(steering:0, brake:0, handbrake:0)` replaces the complete command.
Omitted inputs return to zero. Steering must be finite in [−1,1], brakes finite
in [0,1]; invalid values panic. The command persists until the next call and
takes effect on the next positive active step. A zero step preserves observations;
a disabled chassis preserves steering and wheel rotation.

Positive steering means **the vehicle’s right**, according to its forward/up
frame. With forward +Z and up +Y, right is −X. The geometric angle is
`-steering*maximum_steering_angle` about the local axis; the
`vehicle.wheel(i).steering_angle` snapshot provides it in radians for rendering.

A changed command wakes the chassis; repeating the same command does not.
Steering and brakes at rest do not prevent sleep. The vehicle must be alive,
and mutation must happen outside the world step.

## Observe braking

Both brake inputs add their wheel torques. Braking slows a rotor without
reversing it; when it can lock, the remaining torque holds the wheel locked
against the ground within its tire grip. On a frictionless support, a wheel
can lock while the chassis keeps sliding. In flight, braking affects rotation
without slowing chassis travel.

The snapshot adds `brake_torque`, the actual torque, signed with wheel rotation
and expressed in N·m. Its magnitude stays within the commanded torque budget.
It includes the reaction holding a locked rotor; tire angular damping remains
separate. Existing longitudinal/lateral forces describe contact reactions on
the chassis, with the opposite reaction on the support.

Wheel angle advances after damping and before braking. Velocities, forces and
torques are read after solving. Losing a support clears its contact observations;
the command remains stored for the next step. Destroying the chassis invalidates
controls.

This capability adds steering and brakes to an already moving vehicle; the
powertrain, transmission and their inputs remain future work.

## Behavioral evidence

The [public consumer](../../Tests/Consumer/Tests/VehicleControls3D.sx) checks
stopping in both directions, torque bounds, rear braking, analytic flight,
counter steering, supports, sleep and lifetime. Jolt’s actual wheeled controller
is the reference in Debug/Release at 60/120 Hz on macOS ARM64. Trajectories,
rotations and balances remain checked at every step. Near a stop, slip velocities
are compared; ratios remain checked against their formulas but cross-engine
equality is not claimed when their denominators approach zero. Powertrain,
transmission and execution cost are not qualified by these paths.
