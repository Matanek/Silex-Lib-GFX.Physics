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
sleeping and linear CCD. A virtual
capsule character also walks on fixed convex hulls. See the documentation for
qualified pairs and limits.

```text
silex install GFX.Physics
```

## Documentation

- [French documentation](Docs/FR/README.md)
- [English documentation](Docs/EN/README.md)
- [Release notes](CHANGELOG.md) · [Nouveautés](CHANGELOG.fr.md)

The package requires Silex 0.44.0 or newer.

Combined angle/velocity hinge targets: [English](Docs/EN/HingeCombined3D.md) · [Français](Docs/FR/HingeCombined3D.md).

[3D sliders](Docs/EN/Slider3D.md) guide a carriage along a rotating rail with signed travel and mutable rigid stops.

[Slider motors](Docs/EN/SliderMotor3D.md) drive signed relative speed with bounded force, braking and runtime mutation.

[Slider position servo](Docs/EN/SliderPosition3D.md): target travel, physical spring/damping, bounded force and runtime mutations.
