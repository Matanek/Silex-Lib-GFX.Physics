# Reconstruction corpus and budgets

[Qualified vehicle profiles](VehicleQualification3D.md) summarize available capabilities and their limits. The detailed campaigns below retain their own configurations; an initial witness does not replace later compositions.

This protocol defines the evidence for the native Silex 2D physics
reconstruction. Each result identifies the OS, architecture, CPU, commits,
build mode, worker count, fixed step and repetitions. Time and memory budgets
apply only to the reference macOS ARM64 machine; they do not predict x64
results.

Correctness runs in Debug and Release. Release measurements use one warm-up
followed by seven separate processes and report the median, range and median
absolute deviation. Correctness is a hard gate: a faster run cannot justify
invalid containment, overlap, finite state or determinism.

## Shared scenes

The corpus covers a falling reference body, sparse scenes of 1,000, 5,000 and
10,000 boxes, a stack of 1,000 boxes and containers holding 1,800 and 5,000
awake circles. Each scene fixes dimensions, initial order, materials, gravity
and time step. Silex need not reproduce Box2D's exact floating-point bits.

## Direct Box2D performance comparison

Run `Corpus2D.sx` with `--box2d-parity` when comparing the two engines. This
mode sets gravity to −10 m/s² (zero in sparse scenes), contact stiffness to
30 Hz and each dynamic body's mass to 1 kg. Sparse and circle scenes disable
sleep for the world and the bodies. Without this option, the corpus retains its
historical Silex settings for regression checks; those times cannot be
compared directly with Box2D.

After warming up each executable, alternate seven processes per engine on the
same machine, in Release, with matching substeps and worker counts. Keep the
measured output, excluding the warm-ups, then run:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CompareCorpus.py box2d.log silex.log
```

The checker requires the `box2d-3.1.1-v1` workload marker, equivalent
configurations, physical invariants, determinism for each engine and a MAD no
greater than 5%. It reports the Silex/Box2D median-time ratio and fails above
1. Overlapping timing ranges are inconclusive: refine the experiment instead
of treating noise as an allowed slowdown. It compares one scene and
configuration per invocation; it does not replace the build-option audit or
the full differential correctness corpus.

This gate proves only the configurations actually measured. The Box2D witness
accepts one, two and four workers through its benchmark task adapter, so
multi-worker results also require matching counts. Meeting an absolute budget
does not prove direct performance parity.

## Historical regression budgets

On the reference machine, the limits range from 4 ms per step for 1,000 sparse
bodies to 33.33 ms for 10,000 sparse bodies or the stack. Circle scenes target
16.67 ms. A median that regresses more than 5%, or dispersion above 5%, fails
even below an absolute limit.

Measure process RSS separately from simulation time. After subtracting the
paired reference scene, each sparse dynamic body has a 1 KiB allowance; a
dense scene adds 512 bytes per persistent pair. These are ceilings, not
allocation targets.

## GFX sentinels

Boids2D protects 2D throughput; WorldRendering3D requires at least 120 FPS in
its reference configuration; ShapeGallery2D checks construction, text,
rendering and diagnostics. Automated smokes do not replace an explicitly
requested visual acceptance. These gates do not take automated screenshots.

Raw results are dated under `Benchmarks/Baselines/` and identify the exact
commits. Replacing an accepted baseline requires a green correctness corpus,
admissible variance and explicit review of every changed gate.

## 3D tracked vehicle qualification

`Silex-Benchmarks/Sources/Physics3D/TrackedGroundRun.py` compares pinned Jolt
5.6.0 against the Silex Native Debug/Release SDK on macOS ARM64, one worker,
one substep and 12/4 iterations, at 60/120 Hz. Sixteen airborne cases produce
5,792 states per engine/mode; six ground cases produce 8,652. Each ground case
has 2 s of braked landing, 2 s of driving and 4 s of braking. A Jolt initial
height perturbation of 1 micrometer checks conditioning alongside parity.

Pointwise chassis bounds remain 0.05 m, 0.1 m/s, 0.02 rad and 0.15 rad/s.
Per-step balances allow 0.1 N·s and 0.1 N·m·s; wheel angles are checked to
0.0001 rad, angular velocities to 0.0001 rad/s and RPM to 0.02. Over command-aligned 1 s windows, resultant
forces are bounded by 20 N and 30 N·m, individual mean normal loads by 20 N,
and rotation increments by 0.1 rad. Recovery requires six 163.5 N supports,
981 N total load, 0.88365 m height and speed below 0.05 m/s. Zero grip keeps
the chassis still despite spinning tracks.

Tangential force sharing between six contacts is not unique: individual parity
is not claimed. Left/right mirroring retains pointwise poses but compares 1 s
mean velocities against the same bounds, because Jolt's contact order briefly
exceeds 0.1 m/s. Main Silex/Jolt parity remains fully pointwise. Jolt retains
an earlier unsupported-wheel velocity; the SDK publishes final track velocity.
Checks respect each observation boundary and retain raw data. Both engines'
floating text values are decoded as binary32.

632 corruptions are rejected across both modes and engines. The report records
output hashes and errors; Debug/Release are bit-identical for these cases.
This qualifies the specified ideal tracks, ray contacts and plane, without
claiming articulated links, all terrain coverage or an FPS budget.

## Motorcycle balance qualification

`Silex-Benchmarks/Sources/Physics3D/MotorcycleReferenceRun.py` qualifies the
pinned Jolt 5.6.0 reference; `MotorcycleRun.py` compares its public Silex
consumer. Sixteen 4 s recipes at 60/120 Hz produce 11,552 states per engine/mode,
with one worker, one substep and 12/4 configured iterations, Native Debug/Release
on macOS ARM64. The 100 kg chassis has isotropic inertia 100 kg·m², two 0.3 m
wheels at ±1 m, travel 0.2–0.6 m, springs 10000 N/m and damping 1000 N·s/m.
Engine torque is zero. Turns start at 5 m/s, airborne steering at ±20 m/s.
Turn grip is 1/0.15; the other recipes have no tangential grip.

Pointwise chassis budgets are 0.05 m / 0.1 m/s / 0.02 rad / 0.15 rad/s.
Unassisted fall parity stops pointwise when either center first drops below
0.2 m, then requires the fall and bounded state; 11,009 states remain compared
pointwise. Silex's slope filter is suspension-relative; `pi/2-1e-6` on this
plane preserves the same contacts as Jolt's world-vertical filter. Other
defaults remain unchanged.

Independent checks reconstruct the target from previous forces, the steering
limit, PID torque and wheel velocity compensation. Bounds are 3e-6 rad
steering, 3e-4 target distance, 0.1 N·m·s PID impulse, 0.005 N·s linear balance
and 3e-5 m position per step. The instrumented reference also checks 3e-6 m/s
compensation and integral decay per solver call. Its 19 guards and the
consumer's 16 guards reject corruptions per mode. Native Debug/Release outputs
are identical.

The spring's geometric coefficients remain fixed for the entire step,
including solver visits after pose integration. Smoothing stays per step;
integral decay follows actual solver calls, whose count may differ between
Jolt and Silex. Parity covers physical observations without requiring identity
of those private caches. Assistance is an external actuator with no opposite
support reaction. This campaign covers ray contacts on a plane, balance and
coasting turns; it does not yet qualify composed propulsion, every detector or
terrain, or CPU/GPU cost. Report: `motorcycle-qualification.json` in the group
or workspace's `.silex/physics3d-oracle/` cache.

Silex retains the signed wheel convention: the limit bounds amplitude even
with a negative maximum angle or reversed axis. These cases are checked
analytically. The pinned Jolt controller lets these representations bypass
its limit; parity recipes use Jolt's positive conventions.
