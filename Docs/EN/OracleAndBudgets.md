# Reconstruction corpus and budgets

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
