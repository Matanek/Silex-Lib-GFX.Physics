# World2D performance contract

Performance is measured from executable consumer programs, in Release mode,
after compilation. Compilation time and the Zig cache are not part of a physics
measurement.

```text
silex run Packages/GFX.Physics/Benchmarks/World2D.sx --release
silex run Packages/GFX.Physics/Benchmarks/Scale2D.sx --release
```

`Scale2D.sx` enables four persistent workers. Its sparse case keeps every body
awake and moving without generating contacts; it measures integration, proxy
maintenance, and pair discovery independently of the solver. Its pile case adds
oriented contacts, friction, warm starting, eight velocity iterations, and
contact-island sleep.

The current budgets are:

| Scenario | Budget per step | Current status |
| --- | ---: | --- |
| 1,000 moving, sparse | 4 ms | Met |
| 5,000 moving, sparse | 16.67 ms | Met |
| 10,000 moving, sparse | 33.33 ms | Met |
| 1,000-body settling pile | 33.33 ms | Met |

Reference measurements from the 2026-08-20 `arm64` development machine were:

| Scenario | Total/step | Motion | Broad phase | Solve | Sleep |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1,000 moving, sparse | 1.59 ms | 1.41 ms | 0.18 ms | <0.01 ms | <0.01 ms |
| 5,000 moving, sparse | 8.27 ms | 7.39 ms | 0.88 ms | <0.01 ms | <0.01 ms |
| 10,000 moving, sparse | 17.16 ms | 15.31 ms | 1.85 ms | <0.01 ms | <0.01 ms |
| 1,000-body settling pile | 10.76 ms | 0.42 ms | 2.46 ms | 7.52 ms | 0.36 ms |

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

The next dense-scene milestone is a persistent constraint graph with
conflict-free colors so independent contacts can solve in parallel. SIMD is a
separate backend milestone: the data is already arranged for vector kernels,
but scalar Silex code must not pretend to provide explicit SIMD guarantees.

The graphical `FallingBody.sx --smoke --stress-600` scenario is also measured
separately because it includes ECS synchronization and rendering. Its squares
deliberately create independent Canvas values through the ordinary component
constructor. Scene2D interns equivalent vector geometry internally, reducing
the scene to 6 draw calls without a batching API in the example. On the same
reference machine, the 600-frame smoke averaged 107 FPS and 1.17 ms of physics
work per rendered frame. At its final settled sample all 600 dynamic bodies
were asleep, the active-pair count was zero, and the complete physics step cost
0.45 ms. These are end-to-end application measurements rather than a
physics-only contract. During settling, dense awake contacts remain the next
physics bottleneck.
