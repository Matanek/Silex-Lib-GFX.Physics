# Part 16 ARM64 resident float materialization

Compiler `d1c446c` follows the scalar-square-root candidate `fdeca14`.
Architecturally representable nonzero float32 and float64 constants now use one
scalar `FMOV #imm` directly in their assigned register. Other constants keep
their exact integer bit construction but move directly into their destination
instead of passing through a temporary SIMD register. Inline `copysignf` and
`copysign` operands and results also remain in scalar floating-point residences
around the existing exact sign-bit operation.

Unallocated values and unrepresentable bit patterns keep their prior stack and
integer paths. Zero constants retain their dedicated vector-zero path. Opcode
and expansion tests cover both precisions, representable constants and rejected
patterns.

Static ARM64 code shrinks across all three families:

| Function | Bytes | Instructions |
| --- | ---: | ---: |
| Contact function 0 | 3,136 → 3,116 | 784 → 779 |
| `integrate_velocity` | 620 → 512 | 155 → 128 |
| `integrate_position` | 316 → 296 | 79 → 74 |
| Preparation `prepare` | 2,960 → 2,892 | 740 → 723 |
| Preparation function 1 | 1,660 → 1,448 | 415 → 362 |

The [machine-readable record](2026-09-04-spec16-arm64-resident-float-materialization.json)
contains the three exact campaigns. Each excludes one warmup and alternates
seven serial processes per binary. All samples exceed 20 ms and every MAD is
below 1.3%.

| Family | Silex before | Silex after | Clang slots8 | Silex/Clang |
| --- | ---: | ---: | ---: | ---: |
| Contact normal/friction | 191.775 ms | 192.276 ms | 36.857 ms | 5.2168 |
| Body integration | 953.582 ms | 900.610 ms | 49.740 ms | 18.1064 |
| Constraint preparation | 2,411.129 ms | 2,386.409 ms | 214.527 ms | 11.1240 |

Every before/after range overlaps. Contact is neutral at +0.26%. Integration
and preparation show median decreases of 5.56% and 1.03%, but these timings are
recorded as inconclusive rather than demonstrated gains. The structural
reductions and semantic results are stable.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. `zig build test -Doptimize=Debug` passes 158 language cases and all
compiler, unit and native tests. The ReleaseFast optimizer gate passes 10 fixed
regressions, 8 generated native scenarios, 128 deterministic programs, 32 LLVM
differential programs and its default comparison.

This commit changes only ARM64 encoding and allocation; X64 output is
unchanged. The cumulative portable optimizer work still needs its exact Linux
X64 and Windows X64 native workflow. All ratios remain above one, so Part 16
remains active and `complete-part` must not be called.
