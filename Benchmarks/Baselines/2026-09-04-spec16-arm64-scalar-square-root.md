# Part 16 ARM64 scalar square root

Compiler `fdeca14` follows the scalar-reference candidate `ea38bcc`. Exact
system `sqrtf` and `sqrt` signatures now lower to ARM64 `FSQRT`. Their operands
and results use ordinary scalar floating-point residences, so surrounding live
values no longer inherit the four-register restriction required around an
actual C call.

The specialization is limited to a recognized system provider, exact unary
float32/float64 signatures and a consumed result. Unrelated providers,
mismatched signatures, ignored results and every other math operation retain
their calls. Existing constant evaluation already treats these square roots as
pure IEEE operations. Native regressions cover both precisions, exact opcode
words, zero external-call sites, scalar residence and exact results for signed
zero, finite values, infinity and quiet NaN.

Integration changes substantially:

| Function | Bytes | Instructions | Loads | Stores | Calls |
| --- | ---: | ---: | ---: | ---: | ---: |
| `integrate_velocity` | 1,056 → 620 | 264 → 155 | 73 → 22 | 63 → 13 | 1 → 0 |
| `integrate_position` | 448 → 316 | 112 → 79 | 22 → 11 | 23 → 13 | 1 → 0 |

The complete contact and preparation disassemblies are unchanged. Their
qualified same-layout ratios remain 5.1996 and 11.2726.

The [machine-readable record](2026-09-04-spec16-arm64-scalar-square-root.json)
contains the exact integration campaign. It excludes one warmup and alternates
seven serial processes per binary. All samples exceed 20 ms and every MAD is
below 1%.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex after | 902.435 ms | 892.642–954.567 ms | 0.517% |
| Silex before | 1,284.489 ms | 1,279.182–1,331.515 ms | 0.413% |
| Clang slots8 | 49.115 ms | 48.007–50.349 ms | 0.951% |
| Clang packed4 | 47.355 ms | 46.338–47.926 ms | 0.650% |

The before/after Silex ranges are disjoint. Scalar square-root lowering reduces
integration by **29.744%** and leaves a same-layout ratio of **18.3739**.

The short and complete 32,768-record integration comparisons pass against
Box2D. `zig build test -Doptimize=Debug` passes 158 language cases and all
compiler, unit and native tests. The ReleaseFast optimizer gate passes 10 fixed
regressions, 8 generated native scenarios, 128 deterministic programs, 32 LLVM
differential programs and its default comparison.

This commit changes only ARM64 allocation and encoding; X64 output is
unchanged. The cumulative portable optimizer work still needs its exact Linux
X64 and Windows X64 native workflow. All three ratios remain above one, so Part
16 remains active and `complete-part` must not be called.
