# GFX.Physics

`GFX.Physics` provides optional native Silex 2D and 3D physics simulations.
Their worlds work without windows or renderers; Application plugins connect
them to ECS and Scene2D or Scene3D when requested.
[Fixed attachments](Docs/EN/Fixed3D.md) assemble bodies with a complete relative pose.
The 3D world supports
spheres, boxes, capsules, cylinders, tapered cylinders, tapered capsules and
convex hulls as fixed, kinematic or dynamic solids, plus compounds of these
shapes and fixed triangles, planes or meshes. Round solids retain continuous collision
boundaries and geometric mass properties. Qualified terrain pairs preserve
simultaneous valley supports and merge duplicate seam or ridge reactions.
Public translation sweeps and filtered world queries accompany rigid or spring
distance constraints, point joints and hinges with hard stops, torque-limited
velocity/position motors with symmetric or signed effort bounds, optional soft stops and passive axis friction, contact events,
sleeping and linear CCD. Virtual capsule characters walk, resize and push dynamic objects.
[Physical capsule characters](Docs/EN/PhysicalCharacter3D.md) use the rigid solver
with real mass and locked rotations. See the documentation for
qualified pairs and limits.

```text
silex install GFX.Physics
```

[Parallel 3D simulation](Docs/EN/Parallel3D.md) distributes independent physical work while preserving deterministic body calculations.

## Documentation

- [French documentation](Docs/FR/README.md)
- [English documentation](Docs/EN/README.md)
- [Release notes](CHANGELOG.md) · [Nouveautés](CHANGELOG.fr.md)

The package requires Silex 0.47.1 or newer.

Combined angle/velocity hinge targets: [English](Docs/EN/HingeCombined3D.md) · [Français](Docs/FR/HingeCombined3D.md).

[3D sliders](Docs/EN/Slider3D.md) guide a carriage along a rotating rail with signed travel and mutable rigid stops.

[Slider motors](Docs/EN/SliderMotor3D.md) drive signed relative speed with bounded force, braking and runtime mutation.

[Slider position servo](Docs/EN/SliderPosition3D.md): target travel, physical spring/damping, bounded force and runtime mutations.

[Slider axial friction](Docs/EN/SliderFriction3D.md): passive braking, mutable capacity, signed effort and motor precedence.

[Signed slider force bounds](Docs/EN/SliderForceBounds3D.md): different effort in each direction, velocity and position modes, including one-sided motors.

[Soft slider stops](Docs/EN/SliderSoftLimits3D.md): load compression, physical stiffness/damping and runtime mutation.

[Combined slider position and velocity](Docs/EN/SliderCombined3D.md).

[3D cone joint](Docs/EN/Cone3D.md) · [Articulation cône](Docs/FR/Cone3D.md).

[3D swing and twist](Docs/EN/SwingTwist3D.md) · [Inclinaison et torsion](Docs/FR/SwingTwist3D.md).

[Ragdoll hierarchy and poses](Docs/EN/Ragdoll3D.md) · [Hiérarchie et poses ragdoll](Docs/FR/Ragdoll3D.md).

[Wheel suspension](Docs/EN/VehicleSuspension3D.md) · [Suspensions de roue](Docs/FR/VehicleSuspension3D.md): a dynamic chassis rests, jumps and regains ray, swept-sphere or swept-cylinder supports with tire width; combine it with [passive tire rolling and grip](Docs/EN/PassiveTires3D.md). [Steering and service/hand brakes](Docs/EN/VehicleControls3D.md) are optional; an [engine, transmission and differentials](Docs/EN/VehiclePowertrain3D.md) can power the wheels.

[Six degrees of freedom](Docs/EN/SixDOF3D.md) · [Six degrés de liberté](Docs/FR/SixDOF3D.md).

[3D gear](Docs/EN/Gear3D.md): signed rotational transmission and tracked phase.

[3D rack and pinion](Docs/EN/RackAndPinion3D.md): signed rotation/travel transmission.

[3D pulley](Docs/EN/Pulley3D.md): weighted cable lengths and anchor reactions.

[Spatial hinge and vertical slider](Docs/EN/SpatialRail3D.md): offset loads, gravity, floor contact and reversal with vector reaction balances.

[Anti-roll bars](Docs/EN/VehicleAntiRoll3D.md) couple wheel suspensions to reduce body roll while preserving common heave.
[Vehicle tilt limits](Docs/EN/VehicleTiltLimit3D.md) bound total chassis inclination relative to gravity while leaving yaw free.

[Tracked vehicles](Docs/EN/TrackedVehicle3D.md) · [Véhicules à chenilles](Docs/FR/TrackedVehicle3D.md): drive, turn and pivot with two coupled tracks of suspended wheels.

[Motorcycle balance](Docs/EN/Motorcycle3D.md) · [Équilibre moto](Docs/FR/Motorcycle3D.md): two suspended wheels, independently switchable balance assistance and speed-dependent steering limits.

[Qualified vehicle profiles](Docs/EN/VehicleQualification3D.md) · [Profils véhicules qualifiés](Docs/FR/VehicleQualification3D.md): choose a family, contact detector and validated driving configuration, including current numerical limits.

[Terrain and constraint assembly qualification](Docs/EN/TerrainConstraintQualification3D.md) · [Terrains et assemblages qualifiés](Docs/FR/TerrainConstraintQualification3D.md): supported connections, edited terrains and loaded assembly budgets.
