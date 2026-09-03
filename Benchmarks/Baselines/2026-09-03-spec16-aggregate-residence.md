# ARM64 residences in pure aggregate constructors

Compiler `f4cae16615ed9e6cd9de19c93b8b2f4adf1d5e6a` follows `743ee22`. Pure aggregate constructors and copies
can retain scalar arithmetic values in ARM64 registers without requiring an
unrelated memory operation. Existing ABI homes remain. Arbitrary calls,
escaping addresses and unsupported operations retain the conservative path.

The first eligibility experiment failed the full preparation witness: input
separation was corrupted before the physics calculation. A reduced regression
isolates SIMD affinity that delayed a subtraction beyond its first scalar use.
The existing early-use exclusion now applies to every eligible function,
including pure constructors. The reduced structural check fails before the
correction and passes after, with its native result also checked. The invalid
experiment was never committed or accepted for timing.

The [alternating campaign](2026-09-03-spec16-aggregate-residence.json) uses
macOS 26.6.2 on Apple M3 Pro, one worker, 8,192 constraints and 2,048 passes.
All 26 output fields are observed in the timed reduction. The witness, data,
Box2D revision and Clang flags are unchanged. One warmup is excluded, followed
by seven processes per variant in rotating order; no task-owned build or test
runs concurrently.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 5,710.049 ms | 5,671.145–5,777.416 ms | 0.681% |
| Silex after | 3,672.479 ms | 3,633.400–3,733.568 ms | 0.601% |
| Clang, slots8 | 230.495 ms | 221.365–233.538 ms | 0.364% |
| Clang, packed | 165.488 ms | 163.674–170.208 ms | 1.096% |

The disjoint ranges demonstrate a **35.684% reduction**. The observed
after/before ratio range is 0.62890–0.65834. Silex/Clang remains **15.9330**,
so preparation still fails parity. Historical campaigns are not pooled.

Debug and Release preparation pass all 851,968 full-run field comparisons
with the actual Box2D implementation, maximum Silex error 2.2e-7. Contact and
integration executables reproduce their preceding hashes byte-for-byte when
compiled under their original basenames. Their ratios remain 9.0783 and
29.7626; their correctness evidence and integration FMA diagnostic are unchanged.

The expanded aggregate source fixture passes Debug, Release and interpreter.
Check/test Debug and all 176 Physics tests pass. The correction scene and dense
Release corpus preserve every non-timing dense field from Part 15 exactly.
This corpus run is a correctness control, not an engine speedup measurement.
The complete optimizer-gate and compare 11 pass with a ReleaseFast host tool;
the gate still executes both native Debug and Release. The fixture also emits
Linux/Windows X64 Debug and Release; emission alone is not native validation.

The early-use exclusion is shared by the lane allocator. Native Linux/Windows
validation remains pending; no remote workflow has run. This is a local
compiler candidate, not Part 16 completion. No production Physics solver code
changes. Diagnostic probes and the rejected executable are preserved under
`/private/tmp/spec16-01a06651`; no temporary probe remains in the repositories.
