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

## Build and run

From the workspace root:

```text
cmake -S Packages/GFX.Physics/Benchmarks/Oracle2D -B /tmp/gfx-physics-box2d -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/gfx-physics-box2d --config Release
silex compile Packages/GFX.Physics/Benchmarks/Corpus2D.sx --release -o /tmp/gfx-physics-silex-corpus
```

The CMake configuration fetches only the immutable Box2D commit above. Run a
matching scenario in each executable:

```text
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --release-parity
/tmp/gfx-physics-silex-corpus --release-parity
/tmp/gfx-physics-box2d/gfx_physics_box2d_oracle --circle-1800
/tmp/gfx-physics-silex-corpus --circle-1800
```

The other common options are `--sparse-1000`, `--sparse-5000`,
`--sparse-10000`, `--pile-1000`, and `--circle-5000`. The Silex witness also
accepts `--workers-4`; Box2D remains at one worker until a benchmark-only task
adapter is added. Never compare its one-worker timing to a four-worker Silex
run without naming that distinction.

For Debug correctness, configure the Box2D witness with
`-DCMAKE_BUILD_TYPE=Debug`, compile the Silex witness with `--debug`, and pass
`--debug-build` to the Silex executable so its record names the configuration
truthfully. Debug records carry no cadence budget.

Every run emits one `SILEX_PHYSICS_CORPUS` record. Archive the complete record,
the executable commit, OS, architecture, CPU, compiler version, build mode,
worker count and process peak RSS. Compilation and the initial world/body
construction stay outside `elapsed_ms`; the reported timing contains only the
fixed simulation steps. Box2D uses four substeps per 60 Hz step as recommended
by its public API. The Silex reference uses its public `World2D.step` contract.

`CheckCorpus.py` reads records from files or standard input, checks finite
values, scene invariants and same-configuration signatures, then reports
median, range and median absolute deviation. With seven or more Silex Release
records it also evaluates the cadence budgets. Add `--enforce` when a missed
gate must return a non-zero status; omit it when recording the known misses of
the starting reference.

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
  worker count.
- Box2D and Silex are not expected to have identical floating-point states.
  Compare their scene invariants and trends, not their raw signatures.

The authoritative scenes, invariants, budgets and sentinel protocol live in
[`../../Docs/OracleAndBudgets.md`](../../Docs/OracleAndBudgets.md).
