# World2D performance contract

Performance is measured, never inferred from body count. Benchmarks separate
sparse motion, dense contacts, sleep, joints, workers and rendering cost. See
the [reconstruction corpus and budgets](OracleAndBudgets.md) for the direct
Box2D comparison and its acceptance criteria.

## Run the corpus

From the workspace root, run:

```text
silex run Packages/GFX.Physics/Benchmarks/World2D.sx --release
silex run Silex-Benchmarks/Sources/PhysicsWorldScale2D.sx --release
silex compile Packages/GFX.Physics/Benchmarks/CircleScale2D.sx --release -o /tmp/gfx-circle-scale
/tmp/gfx-circle-scale --count-5000 --long --awake
/tmp/gfx-circle-scale --count-1800 --falling-body --medium --awake
/tmp/gfx-circle-scale --count-600 --falling-body --medium --awake --mixed
silex compile Packages/GFX.Physics/Benchmarks/JointScale2D.sx --release -o /tmp/gfx-joint-scale
/tmp/gfx-joint-scale
/tmp/gfx-joint-scale --workers-4
```

Use Release, one warm-up and isolated repetitions. Compare medians and
dispersion on the same machine. An improvement in one scene does not establish
an improvement for another workload.

## Hot-path architecture

Awake bodies are kept in a reusable contiguous list. A deterministic grid
discovers dynamic candidates and an open set deduplicates pairs. Persistent
contacts retain compatible impulses. The solver prepares contiguous
constraints and partitions them into conflict-free colors.

Parallelism uses a persistent executor. Thresholds of 16,384 active bodies
and 4,096 constraints avoid scheduling small workloads; they never select a
different physical algorithm. The twelfth overflow color remains ordered and
scalar.

Sleep removes settled bodies from the hot path. Bullets and event streams are
opt-in. A stabilized step allocates neither per contact nor per job.

Before a CCD shape cast, `World2D` rejects targets whose bounds do not
overlap the fast body's swept bounds. Those bounds unite its previous and
current positions and include a conservative rotation margin. Distant
targets therefore do not multiply CCD cost in a small scene, while pairs
that can meet still take the continuous collision path.

## Public profiling

```silex
world.set_profiling_enabled(true)
world.step(1.0 / 60.0)
let profile = world.step_profile()
print(profile.broad_phase_ms)
```

The profile exposes only `motion_ms`, `broad_phase_ms`, `solve_ms`, `sleep_ms`
and `total_ms`. Enable it only for diagnosis because measuring has a cost.

## Separate simulation and rendering

```text
silex compile Silex-Benchmarks/Sources/FallingBodies2D/Main.sx --release -o /tmp/gfx-falling-body
/tmp/gfx-falling-body --stress-5000 --smoke-30 --awake --batch-4 --immediate --no-panel
/tmp/gfx-falling-body --stress-5000 --smoke-long --render-only --immediate --no-panel
```

Simulation and `render-only` distinguish limits in Physics, Scene2D, Canvas
and GPU. Graphical observations do not replace headless correctness tests.

## Acceptance rules

An optimization preserves determinism across worker counts, handle integrity,
contact stability, physical bounds and the absence of accidental allocations.
Debug measurements serve diagnosis, never cadence budgets. Exact results and
configurations belong in the repository's dated baselines.
