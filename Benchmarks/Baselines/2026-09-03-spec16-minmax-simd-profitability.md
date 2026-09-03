# Scalar min/max and ARM64 lane profitability

Compiler `dcbdcefd0d7a73d21cc000aebcd6efbf4f1ccac0` follows
`f4cae16615ed9e6cd9de19c93b8b2f4adf1d5e6a`. Release replaces exact scalar
`STD.Math.min` and `STD.Math.max` calls with portable float32/float64 operations
before control-flow inlining. The interpreter, LLVM development oracle, ARM64
and X64 encoders implement the source contract explicitly: a sole NaN yields
the other operand, two NaNs yield the right payload, and equal zeros select the
required sign. Other names or signatures remain calls.

The ARM64 lane allocator now rejects an isolated float32 pair in a memory
kernel when separate scalar stores force its result back out of the lanes.
Chains containing another paired binary operation and aggregate returns remain
eligible. The contact kernel previously retained 22 lane values around six
isolated arithmetic trees; the corrected allocation retains none. Structural
tests distinguish that case from the existing profitable chains.

The [raw campaigns](2026-09-03-spec16-minmax-simd-profitability.json) use the
unchanged Part 16 witnesses, Box2D revision and Clang binaries on macOS 26.6.2
ARM64. Each campaign excludes one warmup and runs seven serial processes per
binary in rotating order. All results have MAD below 1% and samples above
20 ms.

| Family | Silex before | Silex after | Clang slots8 | After/before | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact normal/friction | 360.689 ms | 302.524 ms | 39.807 ms | 0.838739 | **7.5998** |
| Body integration | 1,540.693 ms | 1,541.890 ms | 50.640 ms | 1.000777 | **30.4481** |
| Constraint preparation | 3,692.643 ms | 3,701.285 ms | 231.260 ms | 1.002340 | **16.0049** |

The disjoint contact ranges, 301.970–304.125 ms after and
359.559–361.946 ms before, demonstrate a **16.126% reduction**. Integration and
preparation remain unchanged within their observed ranges; no gain or
regression is claimed for them. All three ratios remain above one, so Part 16
parity still fails.

The contact comparator passes 1,280 scalar comparisons with maximum Silex
error 6.4e-7. Integration and preparation pass their short and full Box2D
checks; preparation still compares 851,968 fields and integration still replays
every transition. `zig build check` passes 1,462 tests, the optimizer gate and
`compare 11` pass, the package is valid, 176 Physics tests and 16 kernel runner
tests pass. The dense 5,000-body corpus reproduces all 34 non-timing fields from
the preceding compiler candidate.

The scalar min/max fixture passes macOS Debug and Release and is added to the
Linux/Windows portability workflow. Run
[`33810121895`](https://github.com/Matanek/Silex/actions/runs/33810121895)
checked out this exact compiler commit, but both jobs stopped before compiling
the fixture because the standalone Silex checkout did not provide `STD.Math`.
Compiler commit `38dc99c395853eb8d641a8b0cab49efb63130d9c` corrects the workflow by
checking out STD at pinned commit `5a018305fb470dfe00e94466150b3c04f207e252`
and linking it in the runner workspace. A new remote run is still required
before this compiler candidate has cross-target execution evidence.

Three experiments were rejected and remain only under
`/private/tmp/spec16-01a06651`: aggressive preparation inlining regressed a
single observation from 3,486.629 to 5,973.092 ms; direct ARM64 square root did
not improve integration; removing unchecked bounds diagnostics did not produce
a material contact gain and violated the language contract. None is included
in either repository commit.
