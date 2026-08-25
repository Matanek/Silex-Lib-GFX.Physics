# World2D performance contract

The reconstruction-wide differential scenes, repetition rules, memory gates,
Box2D oracle and GFX sentinels are defined in
[`OracleAndBudgets.md`](OracleAndBudgets.md). This page retains the detailed
profiling history of the current `World2D` implementation.

Performance is measured from executable consumer programs, in Release mode,
after compilation. Compilation time and the Zig cache are not part of a physics
measurement.

```text
silex run Packages/GFX.Physics/Benchmarks/World2D.sx --release
silex run Packages/GFX.Physics/Benchmarks/Scale2D.sx --release
silex compile Packages/GFX.Physics/Benchmarks/CircleScale2D.sx --release -o /tmp/gfx-circle-scale
/tmp/gfx-circle-scale --count-5000 --long --awake
/tmp/gfx-circle-scale --count-1800 --falling-body --medium --awake
```

`Scale2D.sx` enables four persistent workers. Its sparse case keeps every body
awake and moving without generating contacts; it measures integration, proxy
maintenance, and pair discovery independently of the solver. Its pile case adds
oriented contacts, friction, warm starting, the common four-substep Soft Step
graph, and contact-island sleep.

`CircleScale2D.sx` is the dense-circle contract. Its `--awake` option disables
sleep, so the 5,000-body result measures all bodies and contacts on every one of
600 fixed 60 Hz steps. The scene uses circles of radius 0.025 m inside the same
9.2 × 6.0 m box as the graphical reference. `--falling-body` selects the
graphical example's 0.05 m radius and 87-column layout; `--count-1800` makes the
workload from the interactive performance panel reproducible without depending
on emission timing.

The current budgets are:

| Scenario | Budget per step | Current status |
| --- | ---: | --- |
| 1,000 moving, sparse | 4 ms | Met |
| 5,000 moving, sparse | 16.67 ms | Met |
| 10,000 moving, sparse | 33.33 ms | Met |
| 1,000-body settling pile | 33.33 ms | Met |
| 1,800-circle graphical layout, all awake | 16.67 ms | Met |
| 5,000-circle dense pile, all awake | 16.67 ms | Not met |

The current colored Soft Step solver was measured on 2026-08-25 on the idle
`arm64` development machine with Silex `0.41.0` at `a48d2dd`. Each scenario
used its corpus-defined duration, one untimed warm-up, seven isolated Release
runs, and one worker:

| Scenario | Runs | Median | Range | MAD | Maximum overlap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `sparse-1000` | 7 | 0.787 ms | 0.775–0.815 ms | 0.009 ms | — |
| `sparse-5000` | 7 | 4.080 ms | 3.986–4.144 ms | 0.034 ms | — |
| `sparse-10000` | 7 | 8.517 ms | 8.433–8.821 ms | 0.083 ms | — |
| `pile-1000` | 7 | 6.711 ms | 6.675–6.825 ms | 0.018 ms | — |
| `circle-1800` | 7 | 12.641 ms | 12.507–12.741 ms | 0.082 ms | 7.639 mm |
| `circle-5000` | 7 | 53.876 ms | 53.508–54.393 ms | 0.107 ms | 9.012 mm |

The 5,000-circle correction gate is met, but its cadence target is not. A
native sample attributes most remaining time to the constraint stage and shows
large stack frames and aggregate traffic in call-containing hot functions.
This is recorded as a backend optimization target; it is not hidden behind a
second scalar solver or a relaxed overlap threshold.

The separate memory switch gates pass after correcting the corpus ownership.
The first harness retained every `RigidBody2D` class handle merely to inspect
final state, so its 176,406,528-byte and 99,336,192-byte peaks mostly measured
benchmark objects rather than the world. The corrected indexed observer gives
seven-run medians of 5,357,568 bytes for `release-parity`, 12,484,608 bytes for
`sparse-10000`, and 17,350,656 bytes for `circle-5000`. The sparse increment is
712.704 bytes per body. The dense increment is 11,993,088 bytes for 5,000
bodies and 16,194 persistent pairs, below its 13,411,328-byte body-plus-pair
budget. All RSS series have zero median absolute deviation.

The dense gate was amended from a body-only allowance to 1 KiB per body plus
512 bytes per persistent pair. A contact-free scene and a scene retaining more
than three pairs per body do not have the same storage shape; the pinned Box2D
witness already reaches 58,550,880 bytes on `circle-5000`. This correction
keeps the storage ceiling explicit and does not change the still-unmet 16.67 ms
cadence target.

The following measurements describe the retired pre-Soft-Step implementation
and remain only as profiling history:

| Scenario | Total/step | Motion | Broad phase | Solve | Sleep |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1,000 moving, sparse | 1.59 ms | 1.41 ms | 0.18 ms | <0.01 ms | <0.01 ms |
| 5,000 moving, sparse | 8.27 ms | 7.39 ms | 0.88 ms | <0.01 ms | <0.01 ms |
| 10,000 moving, sparse | 17.16 ms | 15.31 ms | 1.85 ms | <0.01 ms | <0.01 ms |
| 1,000-body settling pile | 10.76 ms | 0.42 ms | 2.46 ms | 7.52 ms | 0.36 ms |
| 1,800 circles, radius 0.05 m, all awake | 11.84 ms | 0.45 ms | 0.84 ms | 10.51 ms | <0.01 ms |

That historical 1,800-circle figure is the median of three 300-step runs measured on
2026-08-23. Its positional phase is 8.04 ms per step. The faster 8.01 ms
six-contact-pass/two-global-pass result is retired: sustained graphical
emission exposed intermittent dense-pile collapse. The relaxed
eight-contact-pass/four-global-pass solver avoided pile-wide collapse in three
independent 30-second, 3,000-circle graphical runs. Those runs ended with 7,
13, and 14 awake bodies at 52.46-53.27 physics Hz. It still retains the 60 Hz
all-awake budget at 1,800 circles.

The slow-emission graphical regression uses a 0.02-second spawn interval. A
30-second run emitted 1,639 circles while sustaining 59.98 physics Hz. It ended
with no awake body below -2 m, zero motion in the floor layer and oldest 100
bodies, and 10.27 mm maximum overlap in the active surface. Without the swept
sleeping-circle test, comparable 10-second runs produced 76-99 mm overlap and
over 130 awake bodies below -2 m as fast balls crossed a complete diameter in
one fixed step.

The mixed-shape reference alternates 500 circles and 500 boxes and emits them
over 20 seconds, leaving 10 seconds to settle. On 2026-08-23, three independent
30-second runs sustained 59.93-59.95 physics Hz with a measured capacity of
144.6-154.3 Hz. They ended with 32-59 awake bodies, 5.44-11.85 mm maximum
circle overlap in the remaining active surface, and only
0.000035-0.001216 m/s in the floor layer. Before position projection was capped
relative to collider size, a representative run ended with 790 awake bodies,
29.66 mm overlap, 1.09 m/s floor motion, and a 14.49 ms solve. The bounded
projection is therefore a stability correction as well as a performance win;
the residual active-surface overlap remains an explicit target rather than a
claimed solved case.

The immediately dense `--stress-3000` mixed layout is not yet a met target. Its
current 600-frame run reaches only 8.16 physics Hz (8.83 Hz measured capacity),
with 3,000 awake bodies and 99.24 ms spent in the solve. It deliberately remains
visible here because the 1,000-body progressive result must not be extrapolated
to a fully active 3,000-body mixed pile. The next optimisation target is the
general mixed-contact position phase and its deep-contact convergence.

The former 9.62 ms dense-circle figure predates the current overlap convergence,
boundary containment, and sleep audit. It is intentionally retired and must not
be used as evidence that the 5,000-circle target is met. The correctness-first
solver currently misses the 16.67 ms all-awake budget; a new median will be
published only after native code generation reaches the budget without
weakening the overlap regressions.

These figures are scenario-specific, not a promise that every arrangement of
the same number of bodies has the same cost. Dense overlap increases candidate
pairs and solver constraints. Once an island sleeps, its motion and solve cost
drops sharply.

The profiler is disabled by default. A benchmark or diagnostic panel can enable
it explicitly:

```silex
world.set_profiling_enabled(true)
world.step(1.0 / 60.0)
let profile = world.step_profile()
print(profile.broad_phase_ms)
```

The constraint graph and conflict-free colors are now present and a 4,100-entry
single-color test exercises a real four-worker dispatch. The next dense-scene
milestone is native-code efficiency: reduce stack and aggregate traffic across
hot call boundaries and extend profitable SIMD beyond the current ARM64 lane
pairs. Scalar Silex code must not pretend to provide gains the emitted binary
does not demonstrate.

The graphical reference includes the window, ECS synchronization, rendering,
and presentation. Build it once, then run the sustained 30-second stress
protocol and its shorter render-only control:

```text
silex compile Packages/GFX.Physics/Examples/World2D/FallingBody.sx --release -o /tmp/gfx-falling-body
/tmp/gfx-falling-body --stress-5000 --smoke-30 --awake --batch-4 --immediate --no-panel
/tmp/gfx-falling-body --stress-5000 --smoke-long --render-only --immediate --no-panel
```

The previous graphical figures used an older radius and solver and are retired.
Every reported run must now include `RENDER FPS`, `VISUAL HZ`, and `PHYSICS HZ`,
plus maximum overlap and awake-body diagnostics. Rendering FPS alone is not a
physics-throughput result.

The live diagnostic Canvas is displayed by default, including during bounded
smoke runs, alongside `Plugins.PerformancePanel`. Pass `--no-panel` for
measurements that isolate the physics and rendering workload: rebuilding and
rasterizing diagnostic text reduces the measured frame rate. The stress scene
allows settled circles to sleep by default; pass `--awake` only for an
all-active physics workload. Every smoke run still prints the complete final
statistics to stdout.

The interactive example uses synchronized presentation and one physics step
per published transform snapshot by default. `--immediate` and `--batch-4`
are explicit benchmark controls; neither is enabled silently by a stress mode.
The rendering panel reports submitted application frames as `RENDER FPS`.
The physics panel reports completed fixed steps as `PHYSICS HZ`, simulation
speed relative to the 60 Hz target, and the percentage of render frames that
repeated the previous snapshot. In the default one-step batch, visual snapshot
cadence equals physics cadence and is deliberately not repeated as another live
row. Bounded benchmark output retains `visual Hz`, where it remains useful for
explicit multi-step batches. The panel also separates the complete scheduled cycle, worker
execution, resubmission delay, queue/poll delay, and raw worker capacity. When
physics is overloaded, the visual cadence and time outside the solver are
therefore reported honestly even though the independent renderer remains
responsive.

Interactive emission uses 87 reusable horizontal slots at the top of the
container. Their occupancy is rebuilt once per completed physics batch. This
preserves non-overlapping births without rescanning every existing circle for
each random spawn attempt, which previously introduced quadratic main-thread
resubmission stalls while the container was filling.

The reported `physics Hz` is completed work divided by wall-clock measurement
time. Four-step asynchronous batches can end the bounded run with a partial
interval, so a value just below 60 does not mean that the fixed delta changed:
every executed step is exactly 1/60 s. `physics capacity` is completed steps
divided by measured worker time and expresses whether the engine can sustain
that schedule.
