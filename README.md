# GFX.Physics

`GFX.Physics` provides optional native Silex 2D and 3D physics simulations.
Their worlds work without windows or renderers; Application plugins connect
them to ECS and Scene2D or Scene3D when requested. The 3D world supports
spheres, boxes, capsules, compounds with dynamic mass, and fixed triangles or
triangle meshes against dynamic spheres, capsules and boxes. Boxes retain
simultaneous support on both pans of a qualified valley without duplicating
identical reactions at terrain seams. It also supports
rigid or spring distance constraints,
contact events, sleeping, linear CCD for the qualified pairs, and a virtual
capsule character mover. Other shape families remain under development.

```text
silex install GFX.Physics
```

## Documentation

- [French documentation](Docs/FR/README.md)
- [English documentation](Docs/EN/README.md)
- [Release notes](CHANGELOG.md) · [Nouveautés](CHANGELOG.fr.md)

The package requires Silex 0.44.0 or newer.
