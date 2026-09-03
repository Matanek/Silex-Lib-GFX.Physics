# Part 16: scalar memory access qualification

This qualifies the first compiler slice of Part 16. It does not complete
the Part or establish parity with Clang. Production Physics sources retain
the accepted Part 15 commit `7ed0c851c7c0f04676b8b7e927c1636bc1f340ce`.
The compiler baseline is `bd0e76b6ab494f72e96d409cdd071169237160f3`.
The compiler candidate is `d8f37f3` (all eleven source, regression, workflow
and documentation files committed together).

## Changes and correctness

For flat numeric and boolean structures, Release narrows reconstructed
reference/view writes when the unchanged fields still match the destination.
It can capture projected snapshot fields with scalar reads at the original
read point. Owning collections, escaped values, stale snapshots and
structures containing owned fields retain their existing representation.
Already bounded collection loads retain their native path and SIMD seeds.

A separate ARM64 correction prevents an unused aggregate-copy leaf from
overwriting a live sibling in the same general register. The minimal native
regression fails before the correction and passes after it. The larger
`AggregateFieldStores.sx` witness also fails with the retained Part 15
compiler: a snapshot's first field becomes its fourth field across a branch.
It passes with this slice in native Debug, native Release and the interpreter.

Six optimizer tests cover fresh and stale snapshots, branches, owning-list
copies, negative indices and bounds failures. A native bit-level case retains
negative zero and both quiet and signaling NaN payloads in Debug and Release.
The ARM64 copy regression is separate. The structural write and read
regressions were each run with the corresponding pass disabled and enabled.

`zig build check -Doptimize=Debug`, `zig build test -Doptimize=Debug`, and
`zig build optimizer-gate` pass. The language suite reports 156 tests in 53
files. The gate retains all ten fixed native regressions, differential
scenarios and LLVM comparisons. The Boids contract retains width three,
15 ARM64 lane pairs and six X64 lane pairs in emitted machine IR.
These X64 counts are structural evidence, not native X64 execution.
`zig build optimizer-oracle -- compare 11` also passes on this candidate.

All 176 Physics tests in 28 files and all ten consumer diagnostic scripts
pass. The benchmark comparator has 19 passing unit tests, including a
baseline participating in the same correctness, warmup and alternating series.

## Contact kernel

The [raw campaign](2026-09-03-spec16-scalar-memory-kernel.json) uses macOS
26.6.2 ARM64, Zig 0.16.0 and the same single-thread contact workload as Part 15:
2,048 contacts, 2,048 passes, float32 values and eight-byte field slots.
Clang retains `-O3 -DNDEBUG -ffp-contract=fast`, without fast-math or disabled
SIMD. Box2D remains pinned to
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`.

| Variant | Median | Observed range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 553.788 ms | 551.148–558.018 ms | 0.212% |
| Silex after | 460.676 ms | 456.806–463.373 ms | 0.196% |
| Clang, matching slots | 39.077 ms | 38.256–39.317 ms | 0.389% |
| Clang, packed layout | 38.271 ms | 37.465–38.996 ms | 1.084% |

Each variant has one excluded warmup and seven serial processes, with all
four variants rotating order. No task-owned build or other benchmark ran
during the timing series. The after/before ratio is 0.831864: a 16.814%
reduction, with an observed ratio envelope of 0.818622–0.840742. This envelope
is not a statistical confidence interval. The remaining Silex/Clang ratio
is **11.7889**; the strict parity gate remains `missed`.

Each candidate is compared against the actual Box2D adapter on all 128
intermediate states and 1,280 scalar values. Maximum absolute errors are
6.4e-7 for both Silex versions and 9.5e-7 for the C witnesses, below the
unchanged 2e-6 tolerance. All timed signatures equal 88453969.40002441.

The new compiler also passes the Box2D state comparison with an explicit
Debug kernel binary, with the same 6.4e-7 maximum error.

To repeat, compile `Benchmarks/ContactKernel2D.sx` from the worktree-group
root with both retained compiler versions, then run `RunContactKernel.py`
with `--silex`, `--baseline-silex`, `--clang-slots`, `--clang-packed`,
`--box2d-check` and `--output`. The JSON records the exact executable paths,
hashes, samples, options and source provenance.

## Full-engine impact control

The [engine observations](2026-09-03-spec16-scalar-memory-engine.json) run
`Corpus2D.sx --circle-5000 --box2d-parity` in Release: 5,000 circles, one
worker, four substeps and 300 steps. There is one excluded warmup and seven
processes per compiler version, alternating which version runs first.
No task-owned build or other benchmark ran during this series.

The measured 300-step median changes from 12,360.960 ms to 12,076.049 ms
(41.2032 to 40.2535 ms per step). MAD is 0.472% before and 0.360% after.
The median ratio is 0.976951, but its observed envelope is 0.937679–1.003218.
The ranges overlap, so this is an inconclusive engine speedup.

Every non-timing output field is exactly identical across all runs:
signature -83418950, overlap 16.319561 mm, 5,000 awake bodies, 18,117
persistent pairs and constraints, and 17,947 compact constraints. This is
a compiler impact check. It does not measure Box2D engine parity or RSS.

## Remaining Part 16 work

The preparation and integration algorithm witnesses remain to be added and
qualified. Contact parity is still unmet. Linux X64 and Windows X64 native
execution is pending; producing ELF and PE witnesses does not qualify those
targets. The targeted native workflow includes the aggregate regression in
Debug, Release and the interpreter, and requires external authorization
before any branch push or dispatch. No engine parity or RSS qualification
is claimed by this slice.
