# GFX.Physics differential oracle

This directory builds a benchmark-only executable against the official Box2D
3 reference. It is not a package dependency and no Box2D code is linked into
the GFX.Physics runtime.

## Pinned sources and attribution

| Project | Role | Revision | License |
| --- | --- | --- | --- |
| [Box2D](https://github.com/erincatto/box2d) | Executable 2D differential oracle | `v3.1.1`, `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3` | MIT, Copyright (c) 2022 Erin Catto |
| [Jolt Physics](https://github.com/jrouwe/JoltPhysics) | 3D architecture reference only | `v5.6.0`, `e77f175595e64cb44218cc9d9d56fc365ad0e36a` | MIT, Copyright (c) 2023 Jorrit Rouwe |

The two upstream licenses require preservation of their copyright and license
notices in any substantial copied or adapted portion. Record the upstream
file, pinned revision and Silex destination beside every future adaptation.
Conceptual study without copied code still cites the project and revision in
the relevant design note. Jolt is not built by this corpus and is not a 2D
performance comparator.

## Executable completeness contract

[`CompletenessMatrix.json`](CompletenessMatrix.json) classifies every
`B2_API` symbol from the five stable public headers of the pinned Box2D
revision. The matrix groups C symbols by gameplay capability rather than
copying the C API into Silex. `covered`, `partial`, `planned`, `divergent` and
`excluded` rows respectively require executable evidence, evidence plus a
future Spec, a future Spec, evidence plus a rationale, or an explicit
rationale.

Run the validator against the immutable source checkout:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCompleteness.py \
    --box2d-source /tmp/silex-box2d-v3.1.1
```

The validator checks the revision, version, per-header counts, unique ownership
of all public symbols, evidence paths and required tracking or rationale. The
CMake project also registers it as `gfx_physics_box2d_completeness` for CTest.
See [`../../Docs/Completeness.md`](../../Docs/Completeness.md) for the contract
boundary and current status.

## Build and run

From the workspace root:

```text
cmake -S Packages/GFX.Physics/Benchmarks/Oracle2D -B /tmp/gfx-physics-box2d -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/gfx-physics-box2d --config Release
silex compile Packages/GFX.Physics/Benchmarks/Corpus2D.sx --release -o /tmp/gfx-physics-silex-corpus
silex compile Packages/GFX.Physics/Benchmarks/GeometryOracle2D.sx --release -o /tmp/gfx-physics-silex-geometry
silex compile Packages/GFX.Physics/Benchmarks/BodyControlOracle2D.sx --release -o /tmp/gfx-physics-silex-body-control
silex compile Packages/GFX.Physics/Benchmarks/DynamicShapesOracle2D.sx --release -o /tmp/gfx-physics-silex-dynamic-shapes
silex compile Packages/GFX.Physics/Benchmarks/ContactPoliciesOracle2D.sx --release -o /tmp/gfx-physics-silex-contact-policies
```

The CMake configuration fetches only the immutable Box2D commit above. Run a
matching scenario in each executable:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --release-parity --substeps-8
/tmp/gfx-physics-silex-corpus --release-parity --substeps-8
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --circle-1800
/tmp/gfx-physics-silex-corpus --circle-1800
```

The other common options are `--sparse-1000`, `--sparse-5000`,
`--sparse-10000`, `--pile-1000`, and `--circle-5000`. The Silex witness also
accepts `--workers-2` or `--workers-4`; omitting both keeps one worker. Box2D
remains at one worker until a benchmark-only task adapter is added. Never
compare its one-worker timing to a multi-worker Silex run without naming that
distinction.

The separate geometry witness compares the public Silex algorithms with
Box2D's pinned collision functions. It covers transformed distance, manifold,
ray and shape casts, convex and degenerate hulls, and front/back chain winding:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_geometry_oracle > /tmp/box2d-geometry.txt
/tmp/gfx-physics-silex-geometry > /tmp/silex-geometry.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckGeometry.py /tmp/box2d-geometry.txt /tmp/silex-geometry.txt
```

The checker requires identical case and field sets, finite candidate values,
and a 0.003 absolute cast tolerance; hull records use 0.0001. The oracle target
is benchmark-only and is not a package or runtime dependency.

The body-control witness covers composed and rounded-shape mass and inertia,
center force and torque integration, off-center impulses, fixed rotation,
kinematic targeting, and disable/re-enable contact lifecycle:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_body_control_oracle > /tmp/box2d-body-control.txt
/tmp/gfx-physics-silex-body-control > /tmp/silex-body-control.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckBodyControl.py /tmp/box2d-body-control.txt /tmp/silex-body-control.txt
```

As with geometry, this differential target is benchmark-only and introduces no
runtime dependency on Box2D.

The dynamic-shape witness settles circle, capsule, segment and rounded-polygon
bodies on a polygon floor, then the massive shapes on the solid middle edge of
an open chain. An eighth scenario drives a circle across three internal chain
transitions. Two conveyor scenarios compare the signed linear velocity,
rotation and angular velocity acquired from rest and generated by friction for
a faster rightward circle. Three example-derived regressions additionally
measure capsule impact depth and verify that an initially tilted polygon and
segment settle on supported faces. The Silex and Box2D segment cases receive
the same explicit finite thin-rod mass properties because a segment has no
area-derived mass; segment-versus-chain-segment is not a supported Box2D pair
and is deliberately absent.

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_dynamic_shapes_oracle > /tmp/box2d-dynamic-shapes.txt
/tmp/gfx-physics-silex-dynamic-shapes > /tmp/silex-dynamic-shapes.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckDynamicShapes.py /tmp/box2d-dynamic-shapes.txt /tmp/silex-dynamic-shapes.txt
```

The checker requires the same thirteen cases and finite states. Settled position
and linear velocity use an 0.08 absolute tolerance. The transition case
compares position and verifies that the circle crossed the internal vertices;
its instantaneous velocity and every rotation are recorded for diagnosis
without requiring identical solver phase between the two engines. The
example-derived cases compare impact depth where trajectories are stable and
otherwise enforce the physical invariant: the body is motionless and supported
by a face rather than balanced on an unsupported corner. A supported face must
be level within 5 mm per metre; this rejects a two-point manifold synthesized
across a tilted edge whose upper endpoint has not reached the support.

The contact-policy witness compares custom rejection, pre-solve disabling,
average friction and restitution, and a replacement contact normal:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_contact_policies_oracle > /tmp/box2d-contact-policies.txt
/tmp/gfx-physics-silex-contact-policies > /tmp/silex-contact-policies.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckContactPolicies.py /tmp/box2d-contact-policies.txt /tmp/silex-contact-policies.txt
```

The material and disabled-contact records use a 0.01 absolute tolerance. The
modified-normal position record allows 0.07 because Box2D applies a larger
speculative positional correction while both engines retain the same modified
normal and unconstrained velocity trend.

The collider-snapshot witness compares two-point contact data, body and shape
filtering, begin/end collider identities, and current sensor overlaps:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_contact_snapshots_oracle > /tmp/box2d-contact-snapshots.txt
/tmp/gfx-physics-silex-contact-snapshots > /tmp/silex-contact-snapshots.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckContactSnapshots.py /tmp/box2d-contact-snapshots.txt /tmp/silex-contact-snapshots.txt
```

Metadata and identities match exactly. Both engines must expose two positive,
finite normal impulses; their total uses a 0.35 absolute tolerance to allow
solver-phase differences without accepting a missing contact point.

For Debug correctness, configure the Box2D witness with
`-DCMAKE_BUILD_TYPE=Debug`, compile the Silex witness with `--debug`, and pass
`--debug-build` to the Silex executable so its record names the configuration
truthfully. Debug records carry no cadence budget.

Every run emits one schema-2 `SILEX_PHYSICS_CORPUS` record. Both implementations
name `engine_version`, the pinned `oracle_version` and `oracle_revision`, the
solver configuration and substep count using the same fields. Archive the complete record,
the executable commit, OS, architecture, CPU, compiler version, build mode,
worker count and process peak RSS. Compilation and the initial world/body
construction stay outside `elapsed_ms`; the reported timing contains only the
fixed simulation steps. Both executables use four substeps by default and
accept `--substeps-1`, `--substeps-2` or `--substeps-8`; the Box2D executable
also accepts the explicit `--substeps-4`. The Silex witness exercises the
public `World2D.step` contract rather than a benchmark-only path.

`CheckCorpus.py` reads records from files or standard input, separates each
substep configuration, checks finite values, scene invariants and
same-configuration signatures, then reports
median, range and median absolute deviation. With seven or more Silex Release
records it also evaluates the cadence gates. Add `--enforce` when a missed gate
must return a non-zero status. The explicitly labelled `circle-5000` cadence
target is still reported when missed, but does not turn a correction-valid run
into a failed hard gate.

When every record is preceded by `# run=N rss_bytes=B`, the checker subtracts
the matching `release-parity` median. `sparse-10000` receives 1 KiB per body;
`circle-5000` receives the same body budget plus 512 bytes per
`persistent_pairs` entry. Dense RSS records without that field are rejected.

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCorpus.py results.jsonl
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCorpus.py --enforce candidate.jsonl
```

`CheckSentinels.py` performs the corresponding seven-run, presentation, MAD
and FPS checks for the Boids and World records. The ShapeGallery sentinel is a
functional smoke plus the milestone visual review and therefore has no FPS
record.

## Repetition and comparison

- Run one untimed warm-up followed by seven measured process executions.
- Use the median as the central value and report minimum, maximum and median
  absolute deviation. Keep all seven raw records.
- A timing baseline is admissible only when the median absolute deviation is
  at most 5% of the median. Otherwise stop competing workloads and repeat; do
  not widen a gate around a noisy machine.
- Compare correctness before timing. A scenario fails if any process exits
  unsuccessfully, emits a non-finite value, violates its invariant, or changes
  `state_signature` across identical runs of the same engine, build, target and
  worker count. When one result file contains several worker counts for the
  same Silex configuration, their signatures must also remain identical.
- Box2D and Silex are not expected to have identical floating-point states.
  Compare their scene invariants and trends, not their raw signatures.

The authoritative scenes, invariants, budgets and sentinel protocol live in
[`../../Docs/OracleAndBudgets.md`](../../Docs/OracleAndBudgets.md).
