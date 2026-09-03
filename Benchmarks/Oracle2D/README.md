# GFX.Physics differential oracle

This directory builds a benchmark-only executable against the official Box2D
3 reference. It is not a package dependency and no Box2D code is linked into
the GFX.Physics runtime.

The [native stage witnesses](StageKernels.md) map isolated contact and body
integration cases to the real Physics/Box2D paths, including layout, precision,
FMA replay verification and the separate compiler-parity gate.

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
    --box2d-source /tmp/silex-box2d-v3.1.1 \
    --final
```

The validator checks the revision, version, per-header counts, unique ownership
of all public symbols, evidence paths and required tracking or rationale. Its
final mode also rejects every remaining `partial` or `planned` capability. The
CMake project registers that final gate as
`gfx_physics_box2d_completeness` for CTest.
See [the completeness contract](../../Docs/EN/Completeness.md) for the contract
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
silex compile Packages/GFX.Physics/Benchmarks/ContinuousCollisionOracle2D.sx --release -o /tmp/gfx-physics-silex-continuous-collision
silex compile Packages/GFX.Physics/Benchmarks/WorldQueriesOracle2D.sx --release -o /tmp/gfx-physics-silex-world-queries
silex compile Packages/GFX.Physics/Benchmarks/CharacterMoverOracle2D.sx --release -o /tmp/gfx-physics-silex-character-mover
silex compile Packages/GFX.Physics/Benchmarks/ExplosionOracle2D.sx --release -o /tmp/gfx-physics-silex-explosion
silex compile Packages/GFX.Physics/Benchmarks/JointsOracle2D.sx --release -o /tmp/gfx-physics-silex-joints
```

The CMake configuration fetches only the immutable Box2D commit above. Run a
matching scenario in each executable:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --release-parity --substeps-8
/tmp/gfx-physics-silex-corpus --release-parity --substeps-8 --box2d-parity
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --circle-1800
/tmp/gfx-physics-silex-corpus --circle-1800 --box2d-parity
```

The other common options are `--sparse-1000`, `--sparse-5000`,
`--sparse-10000`, `--pile-1000`, and `--circle-5000`. The Silex witness also
accepts `--workers-2` or `--workers-4`; omitting both keeps one worker. Box2D
remains at one worker until a benchmark-only task adapter is added. Never
compare its one-worker timing to a multi-worker Silex run without naming that
distinction.

The Silex `--box2d-parity` option is required for direct timing comparisons:
it matches gravity, contact stiffness, unit dynamic-body mass and world sleep
settings. Without it, the historical Silex workload remains available but is
labelled separately. Neither mode changes the engine's public defaults.

After a warm-up of each binary, alternate seven measured processes per engine
with identical worker/substep settings. Save their records, then run:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CompareCorpus.py box2d.log silex.log
```

The checker rejects unmatched or historical settings, incomplete series,
invalid physics, nondeterminism, excessive MAD and a Silex/Box2D median ratio
above 1. Overlapping timing ranges remain inconclusive. It accepts one
configuration per scene per invocation; it does not audit host/build metadata
or replace the full differential corpus. Its negative tests run as CTest
`gfx_physics_box2d_comparison_checks`. See the
[comparison protocol](../../Docs/EN/OracleAndBudgets.md#direct-box2d-performance-comparison).

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

The continuous-collision witness drives circle, capsule, segment and rounded
polygon bodies through a thin fixed wall in one step. It also covers relative
motion from a kinematic target and the explicit bullet path to a dynamic
target:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_continuous_collision_oracle > /tmp/box2d-continuous-collision.txt
/tmp/gfx-physics-silex-continuous-collision > /tmp/silex-continuous-collision.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckContinuousCollision.py /tmp/box2d-continuous-collision.txt /tmp/silex-continuous-collision.txt
```

The four fixed-target cases require both solvers to stop at matching TOI
positions within 2 mm. The checker also records three deliberate one-step
response divergences in the pinned oracle: Box2D retains the incoming velocity
after that TOI placement, does not transfer the traversing kinematic target's
motion, and does not transfer the bullet impulse during the same step. Silex
must apply all three responses because they are part of its public completed-
step contract. These classifications are checked explicitly rather than hidden
behind a broad floating-point tolerance.

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

The world-query witness compares AABB and shape overlap, closest ray and shape
casts, point testing, closest point, world bounds, and collider mass data:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_world_queries_oracle > /tmp/box2d-world-queries.txt
/tmp/gfx-physics-silex-world-queries > /tmp/silex-world-queries.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckWorldQueries.py /tmp/box2d-world-queries.txt /tmp/silex-world-queries.txt
```

Fractions and geometry values use a 0.002 absolute tolerance. The collider
record permits 0.021 because Box2D's `b2Shape_GetAABB` includes its 2 cm broad-
phase margin while Silex reports exact geometry bounds.

The character-mover witness compares collision-plane collection, initial
depenetration, and iterative floor-to-wall movement with Box2D's pinned mover
queries and plane solver:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_character_mover_oracle > /tmp/box2d-character-mover.txt
/tmp/gfx-physics-silex-character-mover > /tmp/silex-character-mover.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCharacterMover.py /tmp/box2d-character-mover.txt /tmp/silex-character-mover.txt
```

The checker requires the same three cases, finite values, and a 0.03 absolute
tolerance for geometry. Counts remain diagnostic within one iteration because
Silex exposes stable colliders rather than Box2D's callback records.

The radial-explosion witness compares affected positions, impulse directions,
filter exclusions, and linear attenuation against the pinned Box2D world
explosion:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_explosion_oracle > /tmp/box2d-explosion.txt
/tmp/gfx-physics-silex-explosion > /tmp/silex-explosion.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckExplosion.py /tmp/box2d-explosion.txt /tmp/silex-explosion.txt
```

The joint witness exercises runtime spring, limit and motor mutation plus
completed-step translations, angles and reactions for distance, prismatic,
revolute and wheel families:

```text
cmake --build /tmp/gfx-physics-box2d --target gfx_physics_box2d_joints_oracle
silex compile Packages/GFX.Physics/Benchmarks/JointsOracle2D.sx --release -o /tmp/gfx-physics-silex-joints
/tmp/gfx-physics-box2d/gfx_physics_box2d_joints_oracle > /tmp/box2d-joints.txt
/tmp/gfx-physics-silex-joints > /tmp/silex-joints.txt
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckJoints.py /tmp/box2d-joints.txt /tmp/silex-joints.txt
```

The checker compares the constrained positions and angles within documented
native-solver tolerances, requires finite reactions, and enforces the configured
motor force and torque maxima. Different internal impulse caches are not
treated as public equality.

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

### Isolate compiler cost from engine architecture

`ContactKernel2D.sx` and `ContactKernel.c` implement the same fused,
single-point contact calculation: separation, normal impulse, friction and
rolling resistance. This is an internal diagnostic, not a replacement for
`World2D` or a claim of whole-engine parity. The adaptation is attributed to
the pinned `src/contact_solver.c:b2SolveOverflowContacts`; its MIT notice is
preserved in [Box2D-LICENSE.txt](Box2D-LICENSE.txt).

The short check compares all six velocities and four impulse values after
each of eight alternating bias/relaxation passes for sixteen contacts against
the **actual unmodified Box2D function**. Fixtures include separated and
penetrating contacts, zero inverse mass/inertia, friction clamps, an offset
anchor, delta rotation, tangent speed and rolling resistance. The 2e-6
absolute tolerance covers float32 arithmetic/FMA and decimal output, not
different physical trajectories. Signed zero is compared numerically.

The timing uses 2,048 independent contacts and 2,048 passes, one worker,
float32, and no allocation or output inside the measured kernel. The bodies'
delta positions/rotations remain fixed: this is repeated constraint solving,
not a simulated time interval. All constraints and bodies remain observable
through the final weighted signature. The C helpers reproduce STD.Math's
NaN and signed-zero branches, and body indexing keeps negative-index and
bounds checks. Failure diagnostics themselves are outside the valid workload.

Build three C witnesses with the existing pinned-oracle CMake configuration:

```text
cmake -S Packages/GFX.Physics/Benchmarks/Oracle2D -B /tmp/gfx-physics-box2d -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/gfx-physics-box2d --target gfx_physics_contact_kernel_slots gfx_physics_contact_kernel_packed gfx_physics_contact_kernel_reference
silex compile Packages/GFX.Physics/Benchmarks/ContactKernel2D.sx --release -o /tmp/gfx-physics-contact-kernel
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/RunContactKernel.py --silex /tmp/gfx-physics-contact-kernel --clang-slots /tmp/gfx-physics-box2d/gfx_physics_contact_kernel_slots --clang-packed /tmp/gfx-physics-box2d/gfx_physics_contact_kernel_packed --box2d-check /tmp/gfx-physics-box2d/gfx_physics_contact_kernel_reference --output /tmp/contact-kernel.json
```

These optional targets use a POSIX clock and Clang; they are not part of
the default build. On the current macOS ARM64 backend, every Silex scalar
occupies an eight-byte storage slot. `slots` reproduces those offsets and
strides (State 56 B, Constraint 176 B, Impulses 32 B), while `packed` keeps
four-byte floats. Both retain 64-bit indices. Comparing Silex with `slots`
isolates compilation/runtime overhead; comparing the two C witnesses diagnoses
layout cost. Neither comparison changes the public engine's representation.

Silex Release fuses eligible multiply/add operations. The C timing targets
therefore use `-O3 -DNDEBUG -ffp-contract=fast`, **without fast-math** or
disabled SIMD. The real Box2D reference remains a correctness check and is
not timed by this harness. Its established full-engine build flags are unchanged.

The runner checks correctness before timing, excludes one warm-up per binary,
rotates seven serial processes per variant, checks final signatures and reports
median, range and MAD. A minimum below 20 ms or MAD above 5% makes the timing
inadmissible. The JSON includes raw samples and executable hashes. Use
`--baseline-silex <binary-before>` to include a compiler baseline in the same
seven-process series. It receives the same correctness checks and excluded
warmup; all four variants rotate through the execution order. The report adds
the after/before median ratio and its observed minimum/maximum range, which is
a sample envelope, not a statistical confidence interval. This comparison
does not replace the Clang parity gate. Use
`--check-only` for Debug/correctness validation. `--require-parity` returns 1
unless the measured Silex range is no slower than the same-layout C range;
overlap is explicitly inconclusive. This is a separate diagnostic gate from
the full-engine comparison above. The caller remains responsible for recording
the actual compiler revisions, build flags and machine availability.

The comparator's negative tests run with:

```text
python3 -B -m unittest discover -s Packages/GFX.Physics/Benchmarks/Oracle2D -p TestContactKernel.py
```

### Full-engine campaigns

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
[the corpus and budgets guide](../../Docs/EN/OracleAndBudgets.md).
