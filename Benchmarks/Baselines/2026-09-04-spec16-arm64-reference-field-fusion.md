# Part 16 ARM64 reference field transfer fusion

Compiler `75628fadba8c89c03e65c36d13fa7023fc834813` follows the paired
aggregate-parameter candidate `50084429478dff29d9f490e6a6aeca2e20335a3b`.
The ARM64 encoder now folds a direct structure-field offset into the
immediately following reference load or store when the projected address has
exactly that one use. Additional uses, a control-flow entry at the transfer,
indirect class fields and a store that also consumes the projected reference
retain the explicit address path.

The transformation does not reuse a memory value or move an access. It removes
only the temporary stack materialization of the derived address. Scalar and
aggregate widths, access order, signed zeros and NaN payloads are preserved.
The native regression checks the direct offset encodings and executes float64
payloads through both a field load and a field store.

Static ARM64 code shrinks in the reference-heavy functions:

| Function | Before | After | Reduction |
| --- | ---: | ---: | ---: |
| Contact function 0 | 3,596 B | 3,208 B | 10.79% |
| `integrate_velocity` | 1,384 B | 1,156 B | 16.47% |
| `integrate_position` | 672 B | 516 B | 23.21% |
| Preparation `prepare` | 5,768 B | 5,768 B | unchanged |
| Preparation main | 20,464 B | 20,152 B | 1.52% |

The [machine-readable record](2026-09-04-spec16-arm64-reference-field-fusion.json)
contains the three exact campaigns. Each excludes one warmup and alternates
seven serial processes per binary. Every timing series is admissible, with
samples above 20 ms and MAD below 1.75%.

| Family | Silex before | Silex after | Clang slots8 | Reduction | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact normal/friction | 212.746 ms | 190.830 ms | 36.880 ms | **10.301%** | **5.1743** |
| Body integration | 1,422.372 ms | 1,316.934 ms | 48.710 ms | **7.413%** | **27.0362** |
| Constraint preparation | 3,484.032 ms | 3,009.796 ms | 214.304 ms | **13.612%** | **14.0445** |

All before/after ranges are disjoint. Contact measures 190.060–191.311 ms
after versus 210.707–222.407 ms before. Integration measures
1,313.908–1,326.208 ms after versus 1,421.066–1,438.735 ms before.
Preparation measures 3,001.155–3,148.846 ms after versus
3,434.092–3,539.547 ms before.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. `zig build test -Doptimize=Debug` passes 158 language cases plus unit
and native tests. The ReleaseFast optimizer gate passes 10 fixed regressions,
8 generated native scenarios, 128 deterministic programs, 32 LLVM
differential programs and its default comparison.

This commit changes only ARM64 encoding; X64 output is unchanged. The
cumulative preceding portable optimizer commit still needs its exact Linux X64
and Windows X64 native workflow. All three same-layout ratios remain above 1,
so Part 16 remains active and `complete-part` must not be called.
