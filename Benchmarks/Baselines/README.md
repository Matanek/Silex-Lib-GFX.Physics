# Accepted physics reconstruction baselines

No timing or FPS baseline is accepted yet for the reconstruction sequence.
Runs performed on 2026-08-23 while the reference machine was also running an
interactive game were deliberately discarded because focus, presentation and
CPU/GPU contention made their variance inadmissible.

The first accepted ARM64 record must be captured on the following reference
machine while it is otherwise idle:

- MacBook Pro `Mac15,7`;
- Apple M3 Pro, 12 cores (6 performance and 6 efficiency);
- 18 GB memory;
- macOS 26.5.2 (`25F84`);
- Silex 0.39.1;
- `GFX.Physics` starting reference `89a3cfa`, after functional reference
  `a736486`;
- Release physics measurements, with separate Debug correctness runs;
- immediate presentation for graphical sentinels;
- one discarded warm-up followed by seven isolated measured runs.

Store the raw `SILEX_PHYSICS_CORPUS`, `SILEX_GFX_BOIDS` and
`SILEX_GFX_WORLD` lines in a dated `.jsonl` or `.log` file in this directory.
Do not retain serial numbers, hardware UUIDs, usernames or absolute home paths.
Validate the files with:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCorpus.py baseline-physics.jsonl
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckSentinels.py baseline-gfx.log
```

After review, add `--enforce` for future candidates and pass the accepted
4,000-boid median through `--boids-kernel-baseline`. Record X64 in a separate
file produced on an actual verified X64 machine; never copy ARM64 results into
that slot.

## Infrastructure verification before capture

On 2026-08-23, before accepting any timing baseline:

- the Silex and Box2D `release-parity` scene passed in Debug and Release on
  macOS ARM64;
- the Silex witness was emitted as Mach-O ARM64, ELF X64 and PE/COFF X64;
  only the Mach-O executable was run, so the two X64 artifacts are
  cross-compilation evidence, not tested platforms;
- `silex check` accepted GFX.Physics and GFX.Scene2D;
- the targeted GFX.Physics, GFX.Scene2D and GFX.Canvas suites passed;
- `./silex-dev test-gfx` completed successfully, including all package-boundary
  consumers and compilation of 17 Canvas, Rendering, Scene2D, Scene3D and
  Viewer examples;
- the Canvas text smoke passed and ShapeGallery2D compiled in Release.

The remaining work is deliberately limited to an idle-machine ARM64 capture,
the visual ShapeGallery milestone when required by the Spec sequence, and
native X64 captures on the corresponding verified systems.
