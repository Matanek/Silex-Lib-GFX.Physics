# Terrains and constraint assemblies

Use a [height terrain](HeightField3D.md) for a regular relief edited through
versions, a [fixed mesh](Geometry3D.md) for an arbitrary triangulated surface,
and the constraints below to assemble bodies. Triangulated surfaces retain
their front-face policy; construction alone does not grant dynamic mobility.

## Choose a connection

| Family | Intent and available settings |
| --- | --- |
| [Fixed](Fixed3D.md) | retain relative pose, with local frames and force/torque reactions |
| [Point](World3D.md#connect-two-bodies-at-a-point) | bring anchors together while allowing free rotation |
| [Distance](World3D.md) | length or range, spring frequency and damping |
| [Hinge](Hinge3D.md) | signed angle, stops, springs, motors and bounded torque friction |
| [Slider](Slider3D.md) | signed travel, stops, springs, motors and bounded force friction |
| [Cone](Cone3D.md) | limit relative opening; no motor owned by this family |
| [Swing/twist](SwingTwist3D.md) | cone or pyramid, twist, motors and angular friction |
| [Six degrees of freedom](SixDOF3D.md) | linear and angular axes, limits, springs, motors and friction |
| [Path](Path3D.md) | open or looping Hermite curve, orientation, motor and friction |
| [Gear](Gear3D.md) | couple rotations through a ratio |
| [Rack and pinion](RackAndPinion3D.md) | couple rotation and translation |
| [Pulley](Pulley3D.md) | weighted cable length, ratio and limits |

Motors and springs are not options shared by every family. Each guide defines
its units, frames, effort bounds and mutations. Collisions between connected
bodies still use ordinary filters: choose compatible shapes and anchors
instead of forcing their overlap.

## Qualified terrains

Grids support distinct spacing, both diagonals, per-vertex holes, irregular
reliefs and rigid poses. `with_heights` and `with_holes` create a version;
`set_shape` publishes it. Old results and shapes remain safe. Comparisons with
an exhaustive mesh preserve winning faces, distances, normals and sweeps for
seven volume families, including tapered shapes. Analytical controls on a
65 × 65 sample grid add queries, contacts and registered character support
inside a transformed world.

Silex heights retain `float` precision. The Jolt 5.6.0 witness uses a 16-bit
heightfield and compares edited heights within 0.2 mm, fractions within 5e−5
and normals within 2e−3. Its quantized in-place editing is distinct from
Silex's immutable version contract. Compression settings are not part of
this API; materials are configured on bodies.

Cell selection reduces work for local queries. Some positive distances and
CCD paths remain exhaustive; editing constructs a complete version. No
constant cost or universal throughput is guaranteed.

## Assemble under load

The [combined consumer](../../Tests/Consumer/Tests/TerrainConstraintQualification3D.sx)
adds two assemblies to the isolated family witnesses:

| Assembly | Observations | Position budget at 1/60 s |
| --- | --- | --- |
| Two SixDOF guides and a 1:1 pulley, 2/8 kg masses, ground contact | initial acceleration, length, equilibrium, tension, mutations and body removal | 8 passes |
| Spatial variant with anchors outside the plane and ratio 2 | lateral guide reactions, tension and weighted length | 48 passes |
| A motorized path carrying an obliquely hinged load into a wall | anchor error, support, bounded motor force, reversal and carriage removal | 8 passes |

These assemblies use 24 velocity passes. Budgets belong to the qualified
recipes; they do not guarantee accuracy for every assembly. At eight position
passes the spatial case exceeds the 1 cm residual bound on first impact in
both engines: about 2.2 cm in Silex and 3.2 cm in Jolt. That budget remains
outside the 1 cm qualification; the same bound is retained at 48 passes.
Increasing the budget has a cost to measure in the consuming scene.

Native Debug/Release and Jolt comparisons check 52 observations: heights,
normals, fractions, velocities, positions, tensions, guide reactions, residuals
and removal results. Equilibria are also calculated analytically. Vertical
support on the loaded carriage is averaged over one second and matches the
58.86 N total weight within 1 N. Exact impact phase is not a shared promise
of the two solvers.

Silex mutations clear incompatible reactions; removing a body invalidates its
incident constraints while retaining other bodies. The Jolt oracle explicitly
removes constraints before destroying a body: it controls common physical
states without reproducing the same public handles.

## Replay the evidence

From the workspace root, or the Spec group root containing the same paths:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/TerrainConstraintQualification3D.sx --backend native
python3 Silex-Benchmarks/Sources/Physics3D/TerrainConstraintsRun.py --mode both
```

The second tool requires the benchmark repository and pinned Jolt libraries
prepared by its foundation harness. It checks sources, package resolution,
configurations and output fields. Its self-tests reject missing, duplicate
or non-finite fields and perturb every observation. This functional
qualification does not replace a global performance, parallelism or soft-body
campaign.
