# GFX.Physics

`GFX.Physics` provides optional native Silex 2D and 3D physics simulations.
Their worlds work without windows or renderers; Application plugins connect
them to ECS and Scene2D or Scene3D when requested. The 3D world supports
spheres, boxes, capsules, cylinders, tapered cylinders, tapered capsules and
convex hulls as fixed, kinematic or dynamic solids, plus compounds of these
shapes and fixed triangles or meshes. Round solids retain continuous collision
boundaries and geometric mass properties. Qualified terrain pairs preserve
simultaneous valley supports and merge duplicate seam or ridge reactions.
Public translation sweeps and filtered world queries accompany rigid or spring
distance constraints, contact events, sleeping and linear CCD. A virtual
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
