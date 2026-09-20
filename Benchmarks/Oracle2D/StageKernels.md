# Native compiler witnesses

These development-only kernels separate compilation from engine architecture.
The C witnesses keep Clang `-O3 -DNDEBUG -ffp-contract=fast`, without fast-math,
`restrict`, forced inlining, volatile work or disabled vectorization. Silex uses
Release with its backend and flags recorded. Box2D is pinned at
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`; its unmodified code is invoked only
for correctness, with contraction disabled in that reference build.

| Case | Physics path in `Module/World2D.sx` | Box2D path | Compared operations and cardinality | Storage and precision |
| --- | --- | --- | --- | --- |
| Normal/friction/rolling resolution | `solve_soft_single_collision`, `solve_soft_compact_circle` | `contact_solver.c`, `b2SolveOverflowContacts` | One point, two bodies, accumulated impulses; 2,048 independent contacts × 2,048 passes | State 7 floats, constraint 2 integers + 20 floats, impulse 4 floats; float32 arithmetic; Native 8-byte slots match padded C; LLVM compact structs match packed C |
| Velocity and position integration | `integrate_body_velocity`, `integrate_body_position` | `solver.c`, `b2IntegrateVelocitiesTask`, `b2IntegratePositionsTask`; `b2IntegrateRotation` | Forces, gravity, two damping reciprocals, linear/angular speed limits, normalized rotation and translation; 8,192 bodies × 2,048 passes; two body traversals per pass | Body 7 floats: 56/28 bytes; forces 8 floats + 2 booleans: 80/36 bytes in slots/packed layouts; float32, boolean results exact |
| One-point constraint preparation | `prepare_collision_constraints`, `prepare_circle_collision_constraints` | `contact_solver.c`, `b2PrepareOverflowContacts` | Normal/tangent/rolling effective masses, anchor separation, relative velocity, warm impulses, static/dynamic softness; 8,192 contacts × 2,048 passes | Input 24 floats: 192/96 bytes; prepared result 26 floats: 208/104 bytes, slots/packed; float32 arithmetic, float64 signature accumulation |

The active sources live under `Benchmarks/StageKernels2D/`. The three older
`*Kernel2D.sx` files remain byte-for-byte frozen inputs of the compiler optimizer
oracle, including their historical output labels. Use the active sources below
for new measurements and complete state checks. Kernel arithmetic is identical
to the frozen fixtures; the contact driver also adds full-state check mode.

The Silex binaries report `private` storage instead of assuming a backend
layout. Both runners require `--silex-layout packed4` for the current LLVM
backend or `--silex-layout slots8` for the native backend. Verify this against
the actual compiler layout and record the build flags and executable hash;
the runners cannot discover backend provenance from an arbitrary executable.
An optional baseline also requires `--baseline-silex-layout`. The matching C
variant supplies the parity denominator; the other layout stays diagnostic.
Old binaries hard-coding `slots8` are rejected and must be rebuilt.

LLVM currently uses compact float32 struct fields and emits with
`-fp-contract=off`; native Release can fuse eligible operations. The C timing
variants keep `-ffp-contract=fast`. These are explicit compiler configurations,
not a common FMA guarantee. Numerical replay permits the resulting legal
rounding differences without changing the arithmetic tolerances.

The integration sources implement the same Box2D ordering in both languages.
Production Physics currently damps after adding forces, stores an angle and
composes normalized rotation deltas, and includes center-of-mass adjustment. Box2D damps
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
production step. The 16 input frames occupy 24 MiB with native/slots8 storage
and 12 MiB with LLVM/packed4 storage; the output buffer occupies
1.625/0.8125 MiB. Initialization
and allocation are excluded. There is no forced inlining or anti-optimization
barrier; invariant hoisting and vectorization remain available to both compilers.

Integration fixtures repeat 16 independent trajectories. They include kinematic
mass, nonzero forces/torque, different damping, both speed limits and fast
rotation. Every pass changes body state; the final weighted signature observes
all seven body fields and the capped flag. Initialization, allocations, output
and signature reduction are outside timing. No interaction joins the repeated
trajectories, so the 16-body correctness run covers the timed patterns.

## Numerical verification

`RunContactKernel.py` checks all ten fields for 128 short states and
32,768 long transitions through the pinned Box2D contact solver. Text values
are first read back as float32, so different round-tripping decimal formats
do not create false errors. The original absolute allowance of `2e-6` applies
to every field, including the long replay from identical preceding inputs.
The accumulated total impulse additionally obeys the exact float32 recurrence
`total[n] = total[n-1] + normal[n]`, starting from zero.

The independent long Contact trajectory remains diagnostic: the C witness
with contraction can diverge cumulatively while each local transition passes.
A counterfactual build with `-ffp-contract=off` removes that divergence in the
fixture; this does not establish identical trajectories for arbitrary worlds.
Each timed Contact signature is bound to its own binary's 16 verified final
patterns, repeated 128 times. Its reduction allowance is
`(2 * 10 * epsilon32 * sum(abs(weighted terms)) + 1e-5) * 128`, covering
float32 products/sums and decimal output, not a physical-state tolerance.
The signature must also remain exactly equal across that binary's excluded
warmup and seven measured processes. A state error fails before any timing;
a signature error invalidates the campaign.

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
explicitly selected matching-layout Clang minimum. Use `--require-parity` to enforce that gate.

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
  Packages/GFX.Physics/Benchmarks/StageKernels2D/Integration.sx --backend llvm --release --nocache \
  -o "$ARTIFACTS/integration-release"
python3 -B Packages/GFX.Physics/Benchmarks/Oracle2D/RunStageKernels.py \
  --stage integration --silex-layout packed4 --silex "$ARTIFACTS/integration-release" \
  --clang-slots "$ARTIFACTS/stages/gfx_physics_integration_kernel_slots" \
  --clang-packed "$ARTIFACTS/stages/gfx_physics_integration_kernel_packed" \
  --box2d-check "$ARTIFACTS/stages/gfx_physics_integration_kernel_reference" \
  --output "$ARTIFACTS/integration.json" --require-parity
```

Compile again without `--release` and run with `--check-only` for Debug.
For preparation, build the three `gfx_physics_preparation_kernel_*` targets,
compile `Packages/GFX.Physics/Benchmarks/StageKernels2D/Preparation.sx`, and select
`--stage preparation` with those executables. Use the same measurement gate.
Comparator regressions: `python3 -B -m unittest discover -s
Packages/GFX.Physics/Benchmarks/Oracle2D -p 'Test*Kernel*.py'`.
