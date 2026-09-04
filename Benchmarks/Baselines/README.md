# Accepted physics reconstruction baselines

## Part 16 compiler memory access — 2026-09-03

The [first scalar-memory qualification](2026-09-03-spec16-scalar-memory.md)
records a 16.814% contact-kernel reduction in a single alternating before/after
campaign, with correctness retained. Silex still takes 11.7889 times the
matching-layout Clang time. The full-engine observations are identical, but
their overlapping timing ranges do not demonstrate an engine speedup.
This is a validated compiler slice; Part 16 parity remains open.

The [following stack-layout correction](2026-09-03-spec16-stack-layout.md)
reduces the contact function's frame by 22.60%, with neutral measured timing
and unchanged physical observations. It does not close the parity gap.

The [direct floating-point transfers](2026-09-03-spec16-float-memory.md)
remove 75 emitted contact instructions while preserving exact payloads.
Their overlapping timing ranges leave the speedup inconclusive; the remaining
Silex/Clang ratio is 11.3310.

A later [read-reuse experiment](2026-09-03-spec16-read-reuse-rejected.md)
passed semantic validation but slowed the contact kernel. Its isolated variants
demonstrated no gain either, so the optimization was not retained.

The [unused checked-payload correction](2026-09-03-spec16-dead-loads.md)
retains bounds diagnostics and removes 84 unused loads and 84 stores from the
contact function. Its alternating campaign demonstrates a 19.877% reduction;
the remaining Silex/Clang ratio is 9.0783, still above the parity target.

The [body integration witness](2026-09-03-spec16-integration.md) broadens the
coverage beyond contacts. Its same-layout ratio is 45.3167. Every local step
passes the actual Box2D replay; the separate accumulated FMA trajectory
difference remains explicit. This witness does not establish compiler parity.

The [constraint preparation witness](2026-09-03-spec16-preparation.md) completes
the three-family diagnostic coverage. All prepared fields match Box2D, but the
same-layout ratio is 25.1739. The compiler parity gate remains open in every case.

The [following math-call residence correction](2026-09-03-spec16-math-calls.md)
reduces integration time by 32.995% without changing any checked state. Its
remaining ratio is 29.7626. Contact and preparation binaries are unchanged.

The [pure aggregate residence correction](2026-09-03-spec16-aggregate-residence.md)
reduces preparation time by 35.684% after correcting an early-use SIMD
regression caught by the full witness. Its remaining ratio is 15.9330; contact
and integration binaries are unchanged. Its subsequent native portability
validation is recorded below.

The [native Linux/Windows qualification](2026-09-03-spec16-native-portability.md)
passes on compiler `f4cae16`, including native Debug/Release and interpreter
execution of the aggregate regression. The outstanding targeted portability
check is closed for this candidate; the performance parity gap remains open.

The [scalar min/max and lane-profitability correction](2026-09-03-spec16-minmax-simd-profitability.md)
reduces the contact witness by 16.126%, from 360.689 to 302.524 ms. Its
same-layout ratio falls to 7.5998. Integration and preparation are unchanged
within their observed ranges and remain at 30.4481 and 16.0049 respectively.
All three parity criteria still fail. The first Linux/Windows run on compiler
`dcbdcef` exposed a missing pinned STD fixture dependency before native
execution. Its [final native portability qualification](2026-09-04-spec16-minmax-native-portability.md)
records the subsequent X64 unordered-comparison correction and a successful
exact-SHA run on Linux and Windows, in Debug and Release. This closes the
candidate's portability check; it does not change the three performance ratios.

The [mutable-view reference correction](2026-09-04-spec16-mutable-view-reference-reuse.md)
then reuses the two checked destination element references and removes dead
checked snapshots around six contact-field writes. Its alternating campaign
reduces contact from 290.448 to 224.655 ms, a demonstrated 22.652% reduction;
the same-layout ratio falls to 5.9574. Integration and preparation remain
neutral in overlapping ranges at ratios 28.8988 and 16.2913. The candidate is
locally green; its exact Linux/Windows portability run remains pending and all
three Part 16 parity criteria still fail.

The subsequent [ARM64 aggregate-parameter pairing](2026-09-04-spec16-arm64-aggregate-parameter-pairs.md)
halves the 22-leaf contact-constraint prologue transfers and removes 22 native
instructions. Its disjoint alternating ranges demonstrate another 5.472%
contact reduction, from 234.169 to 221.355 ms, for a same-layout ratio of
5.6759. Integration and preparation remain neutral in overlapping ranges.
The complete optimizer gate rejected an earlier two-slot form; the retained
value-aggregate scope passes all gates.

The [ARM64 reference-field transfer fusion](2026-09-04-spec16-arm64-reference-field-fusion.md)
then removes the temporary stack address between a single-use field projection
and its immediately following load or store. Its disjoint alternating ranges
demonstrate reductions of 10.301% for contact, 7.413% for integration and
13.612% for preparation. The same-layout ratios fall to 5.1743, 27.0362 and
14.0445 respectively. Correctness and optimizer gates pass, but all three Part
16 parity criteria remain open.

The [ARM64 aggregate-construction affinity](2026-09-04-spec16-arm64-aggregate-construction-affinity.md)
then coalesces the used leaves of complete aggregate constructors with their
source leaves. Preparation falls from 3,015.105 to 2,472.506 ms, a demonstrated
17.996% reduction, and its same-layout ratio falls to 11.2726. Contact and
integration disassemblies are unchanged at ratios 5.1743 and 27.0362. The
broader form was narrowed after the full suite caught a live/dead sibling
residence change; the retained form passes all gates.

The [ARM64 scalar-reference residence](2026-09-04-spec16-arm64-scalar-reference-residence.md)
then keeps reference parameters and derived references in preserved integer
registers and addresses direct transfers from those registers. Contact is
neutral in overlapping ranges. Integration measures 1,279.779 ms against
1,354.058 ms in the alternating campaign, with a same-layout ratio of 26.3021;
preparation is byte-for-byte unchanged at 11.2726. Correctness and optimizer
gates pass, but every Part 16 parity criterion remains open.

The [ARM64 scalar square-root lowering](2026-09-04-spec16-arm64-scalar-square-root.md)
then replaces exact system `sqrtf`/`sqrt` calls with `FSQRT` and releases the
surrounding floating-point values from call-preserved register pressure.
Integration falls from 1,284.489 to 902.435 ms, a demonstrated 29.744%
reduction, and its same-layout ratio falls to 18.3739. Contact and preparation
disassemblies are unchanged at 5.1996 and 11.2726. Correctness and optimizer
gates pass; all Part 16 parity criteria remain open.

The [ARM64 resident float materialization](2026-09-04-spec16-arm64-resident-float-materialization.md)
then encodes eligible constants with scalar `FMOV #imm`, targets other constant
bit transfers directly, and keeps inline `copysign` values resident. It removes
5 contact instructions, 32 integration instructions and 70 instructions from
the two measured preparation functions. All three alternating timing ranges
overlap, so their median changes remain inconclusive; current same-layout
ratios are 5.2168, 18.1064 and 11.1240. Correctness and optimizer gates pass.

The [dominating mutable-view bounds proof](2026-09-04-spec16-dominating-view-bounds.md)
then keeps the two destination addresses local while using the matching checked
entry references to prove their indices. Contact `solve_contact` falls from
3,116 to 2,620 bytes and from 779 to 655 instructions. Its disjoint alternating
ranges demonstrate a 1.467% reduction, from 191.476 to 188.668 ms, and the
same-layout ratio falls to 5.1295. Integration and preparation disassemblies are
unchanged at 18.1064 and 11.1240. The cumulative native Linux/Windows execution
and all three parity criteria remain open.

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

Two further campaigns compare three binaries in rotating order, with one
excluded warm-up and seven processes per binary. The same configuration and
physical state are retained. Each before/after file includes the campaign's
Box2D observations; validate each file separately, never pool those duplicates.

| Compiler change | Before | After | Box2D | After / Box2D |
| --- | ---: | ---: | ---: | ---: |
| Safe memory SIMD (`18806d5`) | 43.916560 ms | 43.917210 ms | 4.449716 ms | 9.869666× |
| Unused borrowed fields (`9cd1f58`) | 43.831646 ms | 43.260345 ms | 4.438417 ms | 9.746796× |

The [SIMD before](2026-09-03-spec15-simd-before.jsonl) and
[SIMD after](2026-09-03-spec15-simd-after.jsonl) campaign is neutral: it
establishes correctness and non-regression, not a dense-scene speedup.
The [field-load before](2026-09-03-spec15-projected-before.jsonl) and
[field-load after](2026-09-03-spec15-projected-after.jsonl) campaign measures
a 1.303% reduction. Its observed ranges do not overlap; timing MAD is
0.287% before, 0.216% after and 0.095% for Box2D. Ordinary interactive
background activity was present, but no task-owned compilation or test ran
concurrently. The gap to Box2D remains unresolved; neither compiler commit
qualifies the engine for parity or closes its functionality and memory gates.

The separate [RSS qualification](2026-09-03-spec15-projected-memory.jsonl)
also remains red: seven processes per scenario give a 7,667,712 B baseline
and 23,330,816 B dense median. The 15,663,104 B increment exceeds the existing
14,395,904 B body-plus-persistent-pair budget by 1,267,200 B. This series uses
`/usr/bin/time -l`; its times are not pooled with the paired timing campaign.

Removing overwritten aggregate local stores (`86477d0`) has a larger effect
in the next independent three-binary campaign. The [before](2026-09-03-spec15-overwritten-before.jsonl)
and [after](2026-09-03-spec15-overwritten-after.jsonl) series measure
44.528137 ms and 41.907570 ms respectively, a 5.885% reduction. Box2D is
4.534857 ms, so the remaining ratio is 9.241211. MAD is 0.187%, 0.266%
and 0.170%; before/after ranges are disjoint. The exact Silex physical state
is unchanged. This change reduces the contact-recording function from
12,868 to 6,236 bytes and the complete executable by 147,776 bytes.
The earlier RSS qualification belongs to `9cd1f58`; memory must be
requalified on later candidates. No parity or functional-completion claim
follows from this timing improvement.

The subsequent arithmetic-scheduling campaign (`54f08b3`) establishes native
SIMD use in the single-contact kernel, but no dense-scene speedup. The
[before](2026-09-03-spec15-scheduled-before.jsonl) median is 40.549496 ms;
[after](2026-09-03-spec15-scheduled-after.jsonl) is 40.756770 ms (0.511% slower),
with overlapping ranges and MAD of 0.153% and 0.105%. Box2D measures
4.425653 ms, leaving a 9.209210 ratio. All Silex state signatures are identical.
The four-contact kernel still has no SIMD residences despite 2,464 portable
affinity groups; the scheduling change alone does not solve that bottleneck.
No RSS measurement or parity acceptance follows from this campaign.

Aggregate SIMD seeds and arithmetic-affinity dependencies (`bd0e76b`) pass
structural and native regressions, including reversed affinity order. Their
[before](2026-09-03-spec15-affinity-before.jsonl) and
[after](2026-09-03-spec15-affinity-after.jsonl) dense series are neutral:
40.867123 ms versus 40.748820 ms (0.289% lower median, overlapping ranges).
MAD is 0.311% before, 0.196% after and 0.078% for Box2D. The oracle measures
4.436960 ms, so parity still fails at 9.183950 times its step time.
The final four-contact kernel is byte-for-byte identical in disassembly to
`54f08b3`: these compiler extensions do not yet vectorize that real kernel.
Do not infer a dense-scene speedup from the isolated SIMD regression tests.

The final [RSS requalification](2026-09-03-spec15-affinity-memory.jsonl) remains
above budget on `bd0e76b`: seven identical readings per scenario give
7,684,096 B for the baseline and 23,216,128 B for the dense scene. The
15,532,032 B increment exceeds the unchanged 14,395,904 B budget by
1,136,128 B. This is a separate memory series, not a paired timing comparison.

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

## Isolated contact-kernel compiler comparison, 2026-09-03

The later [retained solver qualification](2026-09-03-spec15-stabilization.md)
records the correction gates for the production checkpoint and the comparison
infrastructure. All performance and RSS failures below remain open.

[`2026-09-03-spec15-contact-kernel.json`](2026-09-03-spec15-contact-kernel.json)
is a diagnostic baseline, **not an accepted engine-performance result**.
The [kernel protocol](../Oracle2D/README.md#isolate-compiler-cost-from-engine-architecture)
separates semantic alignment, native compilation cost, and storage layout.

Host: macOS 26.6.2 (25G83), Apple M3 Pro ARM64, 12 cores. Silex 0.43.0
at `bd0e76b6ab494f72e96d409cdd071169237160f3`, Release;
STD 0.21.0 at `5a018305fb470dfe00e94466150b3c04f207e252` from the workspace
user link. Apple Clang 21.0.0 (`clang-2100.1.1.101`),
`-O3 -DNDEBUG -ffp-contract=fast`, no fast-math, SIMD not disabled.
The actual Box2D 3.1.1 correctness reference uses the pinned
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3` sources and the existing
Release `-ffp-contract=off` library. Executable hashes are in the JSON.
No compiler or production-physics source changed for this campaign.

After correctness checks and one excluded warm-up per binary, seven serial
processes per variant ran in rotating order. No task-owned compilation,
test suite or other benchmark ran concurrently; ordinary interactive
background activity remained. Each process solves 2,048 independent
one-point constraints 2,048 times (4,194,304 contact solves), without timed
initialization, allocation or output. All measured variants have exactly the
same emitted final signature.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex, 8-byte scalar slots | 555.709 ms | 532.647–557.701 ms | 0.358% |
| Clang, matching slots | 38.973 ms | 36.815–39.398 ms | 1.090% |
| Clang, compact floats | 38.491 ms | 36.507–39.039 ms | 1.242% |

The same-layout ratio is **14.2588×**. The C layout variants overlap, so this
series does not establish a layout speedup. The compiler gap is independently
reproduced without broad phase, graph coloring, world scheduling or events.
It is not a numerical attribution of the full-engine 9.18× gap: the isolated
kernel is a one-point fused solve, not the current production four-normal path.

Release and explicit Debug pass 1,280 per-pass scalar checks against the real
Box2D function. Maximum absolute differences are `6.4e-7` for Silex and
`9.5e-7` for the FMA-enabled C witnesses. Ten negative/positive checker tests
and the existing eight full-corpus comparator tests pass. With
`--require-parity`, the timing runner correctly exits 1 with
`compiler_parity: missed`; functional validation remains green.

Native inspection on these exact binaries gives a 15,560-byte Silex
`solve_contact` and a 908-byte C function. Silex reserves 6,144 bytes of
local/save stack plus the 16-byte frame record; C needs only that 16-byte
record. These static sizes include cold error handling and do not measure
executed instruction counts. Reconstructed whole aggregates on field stores,
repeated view bounds/address work, and scalar/SIMD/stack transfers are concrete
compiler follow-up targets, not yet measured shares of the slowdown.
No X64 execution or performance claim follows from this ARM64 diagnostic.

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
