# Accepted physics reconstruction baselines

## Matched Box2D diagnostics — 2026-09-03

The [matched starting observation](2026-09-03-spec15-box2d-matched.jsonl)
and [Soft Step schedule candidate](2026-09-03-spec15-box2d-schedule.jsonl)
are not accepted parity baselines. Both use the new `--box2d-parity`
configuration, which aligns gravity, contact stiffness, body masses and sleep.
Historical Silex settings must not be pooled with this workload.

On macOS 26.6.2 ARM64, one worker, four substeps and 5,000 awake circles,
the starting observation gives Silex `45.482350 ms` versus Box2D
`4.392293 ms` per step (`10.355036×`). After aligning the solve/relax
schedule, a separate paired campaign gives `43.574833 ms` versus
`4.391180 ms` (`9.923263×`). Each series has seven processes after warm-up
and MAD below 1%. The two campaigns establish the gap to Box2D; they are not
an alternating before/after Silex optimization campaign.

Physical invariants and per-engine deterministic signatures pass; the direct
performance gate correctly fails. Binary hashes, exact configurations and
the uncommitted engine-candidate status are recorded with the raw data.

## Initial reference — 2026-08-23

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

The original corpus retained one class handle per body and therefore reported
16,932.9 B per body for `sparse-10000` and 18,146.9 B per body for
`circle-5000`. Spec 10 rejected those RSS values as benchmark-owned storage;
they remain here only as historical evidence. The dense body-only rule was
also replaced by the body-plus-persistent-pair gate described below.
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

## Spec 09 active-island observation

[`2026-08-25-spec09-reference.jsonl`](2026-08-25-spec09-reference.jsonl) and
[`2026-08-25-spec09-active-islands.jsonl`](2026-08-25-spec09-active-islands.jsonl)
compare `c6b01ec` with the active-island candidate using the same `e2b68ac`
compiler build. Both use one discarded warm-up followed by seven isolated
Release processes. The contact-free 1,000-body scene keeps every body awake,
so it is the worst case for rebuilding the contiguous active list rather than a
favorable sleeping scene:

| Workers | `c6b01ec` median | Active islands median | Change | Candidate MAD |
| --- | ---: | ---: | ---: | ---: |
| 1 | 0.501942 ms | 0.501425 ms | -0.10% | 1.76% |
| 4 | 1.317367 ms | 1.315783 ms | -0.12% | 2.50% |

Both series retain the exact state signature and pass the 4.00 ms cadence
gate. The active compaction therefore removes sleepers from the motion path
without regressing the established all-awake reference on this machine.

## Spec 10 colored Soft Step candidate

[`2026-08-25-spec10-soft-step.jsonl`](2026-08-25-spec10-soft-step.jsonl)
records the cadence and correction results of the colored Soft Step candidate
with Silex `0.41.0` at
`a48d2dd`. The installed and workspace-built compiler executables had the same
SHA-256. One discarded warm-up precedes seven isolated one-worker Release
processes per cadence scenario; an additional four-worker run verifies the
state-signature matrix for the contact scenes.

| Scenario | Median | MAD | Correction and cadence |
| --- | ---: | ---: | --- |
| `sparse-1000` | 0.787 ms | 1.17% | passes 4.00 ms |
| `sparse-5000` | 4.080 ms | 0.84% | passes 16.67 ms |
| `sparse-10000` | 8.517 ms | 0.97% | passes 33.33 ms |
| `pile-1000` | 6.711 ms | 0.28% | passes 33.33 ms and containment |
| `circle-1800` | 12.641 ms | 0.65% | passes 16.67 ms and 12 mm overlap gate |
| `circle-5000` | 53.876 ms | 0.20% | passes 20 mm overlap gate; misses the explicit 16.67 ms target |

One and four workers retain identical state signatures for `release-parity`,
`pile-1000`, `circle-1800`, and `circle-5000`. The checker returns success with
`--enforce` while reporting the missed `circle-5000` cadence target; that row
is intentionally a target rather than a hard switch gate.

[`2026-08-25-spec10-memory.jsonl`](2026-08-25-spec10-memory.jsonl) completes
the seven-process RSS protocol with `/usr/bin/time -l` after correcting the
corpus: it records body indices and queries package-private world storage
instead of retaining one `RigidBody2D` class handle per body. The rejected
harness had measured 176,406,528 B and 99,336,192 B for the two scenes; the
corrected medians are:

| Scenario | Median RSS | Incremental RSS | Gate |
| --- | ---: | ---: | --- |
| `sparse-10000` | 12,484,608 B | 7,127,040 B, or 712.704 B/body | 1 KiB/body — passes |
| `circle-5000` | 17,350,656 B | 11,993,088 B | 1 KiB/body + 512 B/persistent pair — passes |

The dense run retains 16,194 pairs, so its 13,411,328-byte allowance still
leaves only 1,418,240 B of headroom. This revision is not a waiver around the
implementation: the pinned Box2D witness already reports 58,550,880 B on the
dense scene, proving that a body-only allowance conflated body and contact
storage. The checker now requires `persistent_pairs` for dense RSS records and
passes this baseline with `--enforce` while continuing to report the missed
`circle-5000` cadence target.

## Spec 11 joint-color observation

[`2026-08-26-spec11-joints.jsonl`](2026-08-26-spec11-joints.jsonl) records the
new `mouse-4096` workload on the same MacBook Pro `Mac15,7`, Apple M3 Pro,
macOS 26.5.2 ARM64 host. It uses Silex `0.41.0` at `a48d2dd` and the Spec 11
candidate based on GFX.Physics `a89031b`. Creation is outside the measured
region; each isolated Release process advances 4,096 awake bodies and mouse
joints for 60 steps. One discarded warm-up per worker configuration precedes
seven recorded processes.

| Workers | Median | MAD | Dispatches/process | State signature |
| --- | ---: | ---: | ---: | --- |
| 1 | 54.970 ms/step | 0.12% | 0 | `16773632.0, 0.0` |
| 4 | 60.561 ms/step | 0.35% | 960 | `16773632.0, 0.0` |

The exact signature and the focused correctness test prove that the parallel
joint color executes deterministically. They do not prove a speedup: four
workers are 10.17% slower on this workload because the sixteen joint-stage
dispatches per step cost more than their partitioned work saves. Spec 11 sets
no cadence gate for this new workload, so this is a published optimization
target rather than a waived regression. It must not be generalized to X64 or
to contact-heavy scenes.

## Spec 12 event and CCD isolation observation

[`2026-08-26-spec12-events.jsonl`](2026-08-26-spec12-events.jsonl) compares
the exact pre-Spec-12 worktree with the retained candidate on the same Apple
M3 Pro, Silex `0.41.0` at `a48d2dd`, one-worker Release configuration. The
`sparse-10000` scene contains no fixed obstacle, bullet, sensor or enabled
event stream. Seven isolated processes were recorded on each side; every run
retains the exact `16374087000.0` state signature.

| Revision | Median | MAD | CCD bodies/pairs | Change |
| --- | ---: | ---: | ---: | ---: |
| Before Spec 12 | 8.439 ms/step | 0.37% | `0 / 0` | reference |
| Spec 12 candidate | 8.018 ms/step | 0.81% | `0 / 0` | -4.99% |

The structural `CCD2D` test separately verifies that ordinary slow bodies do
not enter the CCD pair path and that only a bullet expands a sweep to a dynamic
target. Contact, hit, sensor and movement streams are opt-in, so this
contact-free corpus constructs no event payload. This is an ARM64 workload
result, not a general speedup claim.

## Spec 13 single-core switch candidate

[`2026-08-26-spec13-switch.jsonl`](2026-08-26-spec13-switch.jsonl) records the
final local switch candidate based on `3e9b837`, using Silex `0.41.0` at
`a48d2dd`. Each timing series discards one warm-up and then records seven
isolated one-worker Release processes. The raw arrays preserve process order;
every run in a scenario retains the signature published beside it.

| Scenario | Median | MAD | Change from Spec 10 | Gate |
| --- | ---: | ---: | ---: | --- |
| `release-parity` | 0.023242 ms/step | 2.37% | n/a | correction and variance pass |
| `sparse-1000` | 0.791658 ms/step | 0.84% | +0.59% | passes 4.00 ms |
| `sparse-5000` | 3.980625 ms/step | 0.60% | -2.44% | passes 16.67 ms |
| `sparse-10000` | 8.072842 ms/step | 1.11% | -5.21% | passes 33.33 ms |
| `pile-1000` | 6.500400 ms/step | 0.10% | -3.14% | passes 33.33 ms and containment |
| `circle-1800` | 12.496713 ms/step | 0.25% | -1.14% | passes 16.67 ms and 12 mm overlap gate |
| `circle-5000` | 53.174103 ms/step | 0.21% | -1.30% | passes 20 mm overlap gate; explicit 16.67 ms target remains open |

The same file records the seven-process peak-RSS series after compacting the
six opt-in body booleans into one internal flag byte:

| Scenario | Median RSS | Incremental RSS | Change from Spec 10 | Gate |
| --- | ---: | ---: | ---: | --- |
| `release-parity` | 6,373,376 B | n/a | n/a | subtraction anchor |
| `sparse-10000` | 13,615,104 B | 7,241,728 B, or 724.173 B/body | +1.61% | 1 KiB/body — passes |
| `circle-5000` | 18,464,768 B | 12,091,392 B | +0.82% | body plus 16,194-pair allowance — passes |

[`2026-08-26-spec13-gfx.log`](2026-08-26-spec13-gfx.log) contains the exact
sentinel lines from the same acceptance session:

| Sentinel | Median | MAD | Gate |
| --- | ---: | ---: | --- |
| Boids kernel, 4,000 | 83.573 FPS | 0.53% | +4.10% from 80.279 FPS; passes 95% floor |
| Boids example, 2,000 | 689.761 FPS | 0.43% | passes 120 FPS |
| World example, focused | 520.770 FPS | 1.53% | passes 120 FPS |
| ShapeGallery | Release compilation and five-second smoke without diagnostics | n/a | automated smoke passes; final visual review pending |

The isolated 0.5 consumer executes both the complete 0.4 world/body intent and
the GFX catalog aliases. The public Events example also emits matching Mach-O
ARM64, ELF X64, and PE/COFF X64 artifacts; only the ARM64 artifact was executed
locally and reported one sensor begin/end pair, one contact begin/hit pair, and
one movement event. X64 execution remains a release-matrix responsibility.
The legacy discrete impulse and warm-start functions are absent from the
candidate: worker count and workload can no longer select a second solver.

Validate the archived graphical records with:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckSentinels.py --enforce --boids-kernel-baseline 80.279 Packages/GFX.Physics/Benchmarks/Baselines/2026-08-26-spec13-gfx.log
```

Future candidates use `--enforce` and pass the accepted 4,000-boid median
through `--boids-kernel-baseline`. No X64 timing baseline is expected:
portable Silex changes use native GitHub Actions for correctness on the exact
pushed commit instead.

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
