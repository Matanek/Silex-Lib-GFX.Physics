# Physics reconstruction corpus and gates

This contract fixes the evidence required before and during the native Silex
physics reconstruction. It does not change the public API or the current
solver. The immutable external revisions and build instructions are recorded
in [`../Benchmarks/Oracle2D/README.md`](../Benchmarks/Oracle2D/README.md).

## Configurations

Each result names an OS, architecture, CPU, Silex commit, engine revision,
Debug or Release mode, worker count, fixed delta and repetition set. Timing,
memory and scaling baselines belong only to the macOS ARM64 reference machine;
there is no X64 performance baseline and no ARM64 result is presented as an
X64 prediction.

Compiler and runtime optimizations remain portable despite that measurement
scope. After each compiler Spec 02, 03 and 04, and after runtime Spec 05, emit
the affected verified targets, run the correctness corpus on ARM64 and replay
the local performance gates named below. These are intermediate local gates:
do not create or push a commit solely to run the native matrix after each Spec.

The shared remote portability gate is the Spec 05 milestone. On one exact
pushed checkpoint containing the completed Specs 02 through 05, require native
GitHub Actions for macOS ARM64, Linux X64 and Windows X64, plus every other
verified target affected by the sequence. If a verified target is missing from
the workflow triggered by that push, extend that workflow before claiming the
sequence as a general Silex optimization. Until this milestone is green,
describe intermediate X64 results as structural emissions rather than native
verification. CI correctness is not a substitute for the ARM64 performance
baseline, and the ARM64 baseline is not a substitute for native CI
correctness.

Correctness runs in Debug and Release. Cadence and memory gates use Release
after one warm-up, with seven isolated process repetitions. Interactive GFX
sentinels use immediate presentation, a fixed window and their built-in
five-second measurement. Record median, range and median absolute deviation
for every timing or FPS series.

## Shared 2D scenes

| Scenario | Scene and duration | Observable correction gate | Release cadence gate |
| --- | --- | --- | ---: |
| `release-parity` | One 1 m box falls from `(0, 2)` onto a 8 m × 1 m floor; 120 steps at 120 Hz | Final center Y within `[0.495, 0.505]` m and speed at most `0.005` m/s | Informational |
| `sparse-1000` | 1,000 non-sleeping 0.5 m boxes on a contact-free 100-column grid, velocity `(2, 0.25)`; 120 steps at 60 Hz | No contact; centroid displacement `(4, 0.5)` m within `0.001` m | `4.00` ms/step |
| `sparse-5000` | Same scene with 5,000 bodies | Same invariant | `16.67` ms/step |
| `sparse-10000` | Same scene with 10,000 bodies | Same invariant | `33.33` ms/step |
| `pile-1000` | 1,000 frictional 0.4 m boxes in 50 columns on a floor; 240 steps at 60 Hz | No center below `0.195` m; all values finite | `33.33` ms/step |
| `circle-1800` | 1,800 non-sleeping circles of radius 0.05 m in the 9.2 m × 6 m graphical container; 300 steps at 60 Hz | No center below `-2.952` m; maximum circle overlap at most `12` mm | `16.67` ms/step |
| `circle-5000` | Same container with 5,000 non-sleeping circles of radius 0.025 m and 170 columns; 300 steps at 60 Hz | No center below `-2.978` m; maximum circle overlap at most `20` mm | `16.67` ms/step target |

The scene dimensions, initial order, materials, gravity and time step are the
same in `Benchmarks/Corpus2D.sx` and the Box2D witness. Box2D's recommended
four substeps and Silex's current public step are deliberately recorded rather
than disguised as identical solvers. Any future Silex kernel joins this corpus
by emitting the same record and using the same scene definitions.

Correctness is a hard gate. A faster result that violates containment,
overlap, finite-state or same-configuration determinism is rejected. The
Box2D envelope is diagnostic: a Silex result outside it requires explanation,
but Silex is not required to reproduce Box2D's exact floating-point state.

## Performance and memory decisions

The cadence budgets apply only to the macOS ARM64 reference machine. A gate
passes when the seven-run median is within budget and median absolute deviation
is at most 5%. A change also fails when its median regresses more than 5%
against the accepted ARM64 baseline, even if it remains under the absolute
budget. Improvements are reported per scene and never generalized from body
count alone.

Record peak process RSS separately from elapsed simulation time. Until a
portable package allocator counter exists, the memory gate is relative. After
subtracting the `release-parity` process RSS, `sparse-10000` has a budget of
1 KiB per dynamic body. The dense `circle-5000` scene adds 512 bytes per
persistent pair to that body budget; its corpus record must therefore expose
`persistent_pairs`. This separates body storage from the contact graph instead
of pretending that a contact-free world and a world retaining more than three
pairs per body have the same storage shape. Both scenes must also avoid a
greater than 5% regression against their accepted ARM64 baseline.

The pair allowance was fixed from the reconstruction evidence: the original
body-only gate was already contradicted by the pinned Box2D witness, whose
world counter reaches 58,550,880 bytes on `circle-5000`, and the corrected
Silex corpus retains 16,194 pairs. The 512-byte value is a ceiling, not an
allocation target. Box2D's `memory_bytes` remains its own world counter and is
diagnostic, not a substitute for the process RSS comparison.

Debug runs establish behavior and diagnostics only; they do not carry cadence
budgets. Compilation time, CMake/FetchContent work and compiler caches never
enter a physics measurement.

## GFX sentinels

The following gates protect compiler and runtime work outside Physics:

| Sentinel | Protocol | Gate |
| --- | --- | --- |
| `Packages/GFX.Scene2D/Benchmarks/Boids/Silex.sx` | Release, 4,000 boids, immediate presentation, fixed 960 × 640 logical window with high pixel density, one warm-up plus seven five-second runs | Same-machine median FPS must not regress by more than 5%; MAD must be at most 5% |
| `Packages/GFX.Scene2D/Examples/Boids.sx` | Release with `--benchmark`, immediate presentation, seven five-second runs | Median at least 120 FPS; MAD at most 5% |
| `Packages/GFX.Scene3D/Examples/World.sx` | Release with `--benchmark-focused`, focused window, immediate presentation, default scene and window, seven five-second runs | Median at least 120 FPS; MAD at most 5% |
| `Silex-Examples/Sources/ShapeGallery2D/Main.sx` | Compile the centralized application in Release; inspect emitted assertions and renderer diagnostics | More than 50 retained commands, font/text path succeeds, no renderer or shader diagnostic; visual acceptance remains required at milestones named by the Spec sequence |

Do not take automated screenshots for these gates. ShapeGallery's automated
smoke protects construction, text loading and the render path; the explicitly
requested milestone review remains the authority for visual integrity.

Replay the Boids benchmark locally after compiler Specs 02, 03 and 04 and after
runtime Spec 05. Replay all four sentinels locally at the Spec 05 milestone,
then run the shared remote portability gate on the exact checkpoint. Replay
the four sentinels again before the Spec 13 switch.

## Baseline acceptance

Raw results belong in a dated file under `Benchmarks/Baselines/` and identify
the exact Git commits. A local series is a baseline observation, not an
accepted replacement. Replacing an accepted baseline requires a green
correctness corpus, admissible variance and explicit review of every missed or
materially changed gate.

Until the reference machine is idle, `Benchmarks/Baselines/README.md` records
the exact pending configuration without promoting contaminated observations
to an accepted baseline.
