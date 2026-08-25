# Accepted physics reconstruction baselines

The initial ARM64 reference was captured on 2026-08-23 while the machine was
otherwise idle. Earlier runs made while an interactive game was active and a
World series made without window focus were discarded; neither appears in the
raw records.

Reference configuration:

- MacBook Pro `Mac15,7`;
- Apple M3 Pro, 12 cores (6 performance and 6 efficiency);
- 18 GB memory;
- macOS 26.5.2 (`25F84`);
- Silex 0.39.1;
- Silex toolchain commit `b52b54f4dcc48f814a0a258cefd5058df9794951`;
- `GFX.Physics` commit `b453ac9abccfcb0b697ac9704aaac41efac11409`,
  after starting reference `89a3cfa` and functional reference `a736486`;
- Release physics measurements, with separate Debug correctness runs;
- immediate presentation for graphical sentinels;
- one discarded warm-up followed by seven isolated measured runs.

The complete records and per-process RSS observations are stored in
[`2026-08-23-arm64-physics.jsonl`](2026-08-23-arm64-physics.jsonl). This is an
admissible starting observation, not a claim that the current solver passes
every reconstruction gate:

| Scenario | Silex median | MAD | Median RSS | Box2D median | Silex gate |
| --- | ---: | ---: | ---: | ---: | --- |
| `release-parity` | 0.006417 ms/step | 2.99% | 4,128,768 B | 0.001025 ms/step | correction passes |
| `sparse-1000` | 0.459542 ms/step | 0.56% | 20,398,080 B | 0.090200 ms/step | passes |
| `sparse-5000` | 2.189183 ms/step | 1.64% | 88,604,672 B | 0.519224 ms/step | passes |
| `sparse-10000` | 4.484692 ms/step | 0.27% | 173,457,408 B | 1.101243 ms/step | cadence passes; memory fails |
| `pile-1000` | 20.755947 ms/step | 0.64% | 21,676,032 B | 0.220953 ms/step | passes |
| `circle-1800` | 19.815577 ms/step | 0.45% | 34,816,000 B | 0.745873 ms/step | cadence fails |
| `circle-5000` | 101.257370 ms/step | 1.24% | 94,863,360 B | 4.530633 ms/step | correction, cadence and memory fail |

After subtracting `release-parity`, Silex uses 16,932.9 B per body for
`sparse-10000` and 18,146.9 B per body for `circle-5000`, above the 1 KiB gate.
The `circle-5000` state is deterministic but reaches 49.056 mm maximum overlap,
above its 20 mm correction gate. `circle-1800` and `circle-5000` also exceed
their 16.67 ms cadence budgets. All seven-run timing MAD values remain below
5%, so these misses are workload results rather than inadmissible variance.

The graphical records are stored in
[`2026-08-23-arm64-gfx.log`](2026-08-23-arm64-gfx.log):

| Sentinel | Median | MAD | Gate |
| --- | ---: | ---: | --- |
| Boids kernel, 4,000 | 80.279 FPS | 0.39% | baseline anchor |
| Boids example, 2,000 | 237.548 FPS | 1.61% | passes 120 FPS |
| World example, focused | 227.088 FPS | 1.46% | passes 120 FPS |
| ShapeGallery | 28 Canvas tests pass; five-second Release smoke has no renderer or shader diagnostic | n/a | passes automated smoke |

World used `--benchmark-focused`; the lower non-focused series was rejected
before archival. ShapeGallery was not captured visually: its explicitly named
milestone review remains separate from this automated smoke.

Future captures store the raw `SILEX_PHYSICS_CORPUS`, `SILEX_GFX_BOIDS` and
`SILEX_GFX_WORLD` lines in a dated `.jsonl` or `.log` file in this directory.
They must not retain serial numbers, hardware UUIDs, usernames or absolute
home paths. Validate the accepted files with:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCorpus.py Packages/GFX.Physics/Benchmarks/Baselines/2026-08-23-arm64-physics.jsonl
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckSentinels.py --enforce Packages/GFX.Physics/Benchmarks/Baselines/2026-08-23-arm64-gfx.log
```

## Spec 08 broad-phase observation

[`2026-08-25-spec08-broad-phase.jsonl`](2026-08-25-spec08-broad-phase.jsonl)
records the persistent-contact candidate on the same macOS ARM64 machine. It
uses one discarded warm-up and seven isolated Release processes per worker
configuration:

| Scenario | 1 worker median | 4 workers median | Gate |
| --- | ---: | ---: | --- |
| `sparse-1000` | 0.486692 ms | 1.263167 ms | both pass 4.00 ms |
| `sparse-5000` | 2.353458 ms | 7.471250 ms | both pass 16.67 ms |
| `sparse-10000` | 4.984250 ms | 16.072742 ms | both pass 33.33 ms |

The immediately preceding `37c0aab` median for `sparse-1000` at one worker was
0.495917 ms, so the retained scalar path did not regress. Four workers exercise
the dynamic-tree count/prefix/fill path and preserve the exact state signature,
but are slower on these contact-free grids; the observation proves bounded
cadence and deterministic scaling, not a parallel speedup. Every series has a
MAD below 2.09%.

After review, add `--enforce` for future candidates and pass the accepted
4,000-boid median through `--boids-kernel-baseline`. No X64 timing baseline is
expected: portable Silex changes use native GitHub Actions for correctness on
the exact pushed commit instead.

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

The ARM64 starting baseline is complete. The visual ShapeGallery milestone
remains required only where the Spec sequence names it. Future compiler or
runtime optimizations must pass native macOS ARM64, Linux X64 and Windows X64
GitHub Actions on the exact pushed commit, and every other verified target they
affect. The push workflow must be extended first when one of those targets is
missing.
