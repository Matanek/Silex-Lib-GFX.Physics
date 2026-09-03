# Native compiler witnesses

These development-only kernels separate compilation from engine architecture.
The C witnesses keep Clang `-O3 -DNDEBUG -ffp-contract=fast`, without fast-math,
`restrict`, forced inlining, volatile work or disabled vectorization. Silex uses
native Release. Box2D is pinned at
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`; its unmodified code is invoked only
for correctness, with contraction disabled in that reference build.

| Case | Physics path in `Module/World2D.sx` | Box2D path | Compared operations and cardinality | Storage and precision |
| --- | --- | --- | --- | --- |
| Normal/friction/rolling resolution | `solve_soft_single_collision`, `solve_soft_compact_circle` | `contact_solver.c`, `b2SolveOverflowContacts` | One point, two bodies, accumulated impulses; 2,048 independent contacts × 2,048 passes | State 7 floats, constraint 2 integers + 20 floats, impulse 4 floats; float32 arithmetic; Silex 8-byte slots matched by C padding, plus separate packed C |
| Velocity and position integration | `integrate_body_velocity`, `integrate_body_position` | `solver.c`, `b2IntegrateVelocitiesTask`, `b2IntegratePositionsTask`; `b2IntegrateRotation` | Forces, gravity, two damping reciprocals, linear/angular speed limits, normalized rotation and translation; 8,192 bodies × 2,048 passes; two body traversals per pass | Body 7 floats: 56/28 bytes; forces 8 floats + 2 booleans: 80/36 bytes in slots/packed layouts; float32, boolean results exact |
| One-point constraint preparation | `prepare_collision_constraints`, `prepare_circle_collision_constraints` | `contact_solver.c`, `b2PrepareOverflowContacts` | Normal/tangent/rolling effective masses, anchor separation, relative velocity, warm impulses, static/dynamic softness; 8,192 contacts × 2,048 passes | Input 24 floats: 192/96 bytes; prepared result 26 floats: 208/104 bytes, slots/packed; float32 arithmetic, float64 signature accumulation |

The integration sources implement the same Box2D ordering in both languages.
Production Physics currently damps after adding forces, stores an angle and
recomputes its sine/cosine, and includes center-of-mass adjustment. Box2D damps
the old velocity and integrates a normalized rotation pair. The witness does
not change Physics or claim those production paths are algorithmically equal.
The contact witness likewise does not reproduce production batching/scheduling.

Preparation snapshots the two bodies' velocities into its input record instead
of timing their graph lookup. Friction/restitution are already combined, as in
the Box2D contact record. It covers one manifold point; two-point coupling and
production circle batching are excluded. Sixteen prebuilt frames vary anchors,
normal, separation, velocities and impulses. They are revisited cyclically;
16 independent patterns per frame include fixed-body and zero-denominator
diagnostics. The both-fixed case exercises numerical guards, not a reachable
dynamic-world contact. The fixture's zero mass denotes a fixed body, not a
moving kinematic body. Warm start alternates on/off. Scalar `copy` expressions
detach local velocity values from the borrowed input before substituting the
fixed body's zero velocity; they follow the existing borrowing contract.

Each pass prepares its complete output buffer and consumes all 26 fields in a
weighted float32 sum accumulated in float64. **That reduction is timed** and is
identical in C/Silex; it prevents unobserved earlier outputs from disappearing.
The reported case is preparation plus observation, not a measured share of a
production step. The 16 input frames occupy 24 MiB in the Silex/slots8 layout
and 12 MiB packed; the output buffer occupies 1.625/0.8125 MiB. Initialization
and allocation are excluded. There is no forced inlining or anti-optimization
barrier; invariant hoisting and vectorization remain available to both compilers.

Integration fixtures repeat 16 independent trajectories. They include kinematic
mass, nonzero forces/torque, different damping, both speed limits and fast
rotation. Every pass changes body state; the final weighted signature observes
all seven body fields and the capped flag. Initialization, allocations, output
and signature reduction are outside timing. No interaction joins the repeated
trajectories, so the 16-body correctness run covers the timed patterns.

## Numerical verification

`RunStageKernels.py` checks every field in the first eight passes, then all
32,768 transitions of the 16-pattern, 2,048-pass run. For the long run, the
reference replays each transition from the candidate's preceding state through
the actual pinned Box2D tasks. This checks local arithmetic from identical
inputs despite different legal FMA contractions. The unchanged local allowance
is `2e-5 + 2e-6 * abs(reference)`; capped flags must match exactly. Duplicate,
missing, non-finite or malformed records fail before timing.

The independent long Box2D trajectory is also recorded as a diagnostic.
An initial cumulative allowance of `2e-3 + 2e-4 * abs(reference)` was exceeded
by Silex and is retained explicitly as a failed diagnostic, not widened or
reported as trajectory equality. A reduced calculation explains the source:
for damping 0.125, angular velocity -112, inertia 0.25 and torque -7,
`dw + damping * w` gives -111.948997498 without fusion, versus -111.948989868
when the damping multiplication is fused. Clang may instead fuse the torque
multiplication. That one-ulp difference accumulates into the rotation phase.
The replay gate verifies each rounding step; it does not promise identical
long-term orientations across compilers or change a physical tolerance.

Each integration signature is checked against the same binary's fully verified
final states, repeated 512 times. Preparation compares all 851,968 scalar
outputs (2,048 passes × 16 patterns × 26 fields) directly with Box2D, using
`2e-6 + 2e-6 * abs(reference)` throughout. It has no state recurrence or replay
exception; its signature includes every verified pass, repeated 512 times.
The signature allowance covers only float32 reduction and
decimal printing; it is independent of the looser cumulative diagnostic.
One excluded warmup precedes seven serial processes in rotating order.
MAD must be at most 5% and each sample at least 20 ms. Overlapping time ranges
are inconclusive; parity requires the Silex maximum no greater than the
matching-layout Clang minimum. Use `--require-parity` to enforce that gate.

## Reproduction

Run from the isolated Spec workspace root. Supply a clean local checkout of
the pinned Box2D source and choose an external artifact directory:

```sh
cmake -S Packages/GFX.Physics/Benchmarks/Oracle2D -B "$ARTIFACTS/stages" \
  -DCMAKE_BUILD_TYPE=Release -DFETCHCONTENT_SOURCE_DIR_BOX2D="$BOX2D_SOURCE"
cmake --build "$ARTIFACTS/stages" --target \
  gfx_physics_integration_kernel_slots gfx_physics_integration_kernel_packed \
  gfx_physics_integration_kernel_reference
Silex/Toolchain/zig-out/bin/silex compile \
  Packages/GFX.Physics/Benchmarks/IntegrationKernel2D.sx --release --nocache \
  -o "$ARTIFACTS/integration-release"
python3 -B Packages/GFX.Physics/Benchmarks/Oracle2D/RunStageKernels.py \
  --stage integration --silex "$ARTIFACTS/integration-release" \
  --clang-slots "$ARTIFACTS/stages/gfx_physics_integration_kernel_slots" \
  --clang-packed "$ARTIFACTS/stages/gfx_physics_integration_kernel_packed" \
  --box2d-check "$ARTIFACTS/stages/gfx_physics_integration_kernel_reference" \
  --output "$ARTIFACTS/integration.json" --require-parity
```

Compile again without `--release` and run with `--check-only` for Debug.
For preparation, build the three `gfx_physics_preparation_kernel_*` targets,
compile `Packages/GFX.Physics/Benchmarks/PreparationKernel2D.sx`, and select
`--stage preparation` with those executables. Use the same measurement gate.
Comparator regressions: `python3 -B -m unittest discover -s
Packages/GFX.Physics/Benchmarks/Oracle2D -p 'Test*Kernel*.py'`.
