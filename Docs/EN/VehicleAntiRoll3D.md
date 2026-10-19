# Reduce body roll with paired suspension bars

An anti-roll bar couples two wheels of the same vehicle and opposes the
difference in their suspension lengths when both have support. With identical
wheel settings, it increases the reaction on the more compressed side and
reduces the opposite reaction. It preserves common vertical suspension travel and
unilateral forces: wheels never pull the ground.

The [headless example](../../Examples/VehicleAntiRoll.sx) compares the same
chassis under a 40 N·m torque, without bars and then with two bars:

```sh
silex run Packages/GFX.Physics/Examples/VehicleAntiRoll.sx --release
```

After two seconds under load at 120 Hz, the example reports about 2.6°
without bars and 0.44° with bars.
Supply this fragment when creating the vehicle, using previously constructed
chassis and wheel settings:

```sx
Physics.WheeledVehicle3DSettings(chassis, wheels, anti_roll_bars:[
    Physics.VehicleAntiRollBar3DSettings(0,2,stiffness:1000.0),
    Physics.VehicleAntiRollBar3DSettings(1,3,stiffness:1000.0)
])
```

Here wheels are ordered rear left, front left, rear right, front right.
Indices refer to the wheel array, independently of driven wheels and
differentials. No extra update call is required: the world handles bars in
`world.step`.

## Configure and inspect pairs

`VehicleAntiRollBar3DSettings(left_wheel,right_wheel,stiffness:1000.0)` stores
the indices and stiffness in N/m. Zero stiffness disables a bar; omitting bars
preserves previous behavior. Indices must be distinct, nonnegative and present
in the vehicle, and pairs must be disjoint. Stiffness and its product with
suspension travel must be finite. Settings copy the input array at creation.
`anti_roll_bar_count()` and `anti_roll_bar(i)` inspect it on
`WheeledVehicle3DSettings`; an out-of-range index produces a diagnostic.

The transfer contributes to the two implicit spring biases, as in the pinned
Jolt reference. Its response also depends on damping, time step and contact
directions: stiffness alone does not describe an independent torsion spring.
Compare settings at the chosen fixed time step. A missing support disables
that pair for the current step. Ordinary `vehicle.wheel(i)` snapshots expose
the actual solved forces and contacts. Dynamic supports receive opposite
reactions at the same physical points. A zero step preserves observations.

## Evidence and scope

The [public consumer](../../Tests/Consumer/Tests/VehicleAntiRoll3D.sx) checks
copying, independent state, zero stiffness, weight, heave, opposite loaded roll,
missing support, disabling and momentum conservation on a dynamic support.
`VehicleAntiRollRun.py` compares five recipes with and without bars, including
zero stiffness, at 60/120 Hz in Native Debug/Release on macOS ARM64. It checks
per-step balances, the spring law, symmetry, roll reduction, Jolt trajectories
and phase mean forces; guards reject missing, duplicate, nonfinite or corrupt
output.

Bars do not explicitly bound a maximum tilt angle and do not replace motorcycle
balance control. Driving comparisons with tires remain separate from the
frictionless witness. See [suspensions](VehicleSuspension3D.md),
[tires](PassiveTires3D.md) and [controls](VehicleControls3D.md).
