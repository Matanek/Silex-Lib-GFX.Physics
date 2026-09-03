# Part 16 paired ARM64 aggregate parameter transfers

Compiler `50084429478dff29d9f490e6a6aeca2e20335a3b` follows the mutable-view
reference candidate `00aac59ef4aa0221cbec807ee164740ae802ddfc`. The ARM64
prologue now copies consecutive stack-resident leaves of value aggregate
parameters with `LDP`/`STP`. Resident leaves, odd tails and offsets outside the
pair encoding retain their scalar path.

An initial broader prototype also paired two-slot aggregates. The optimizer
gate caught a Release mismatch in `BoundedCollectionLoop.sx`, because that
machine-level category includes collection-view ABI descriptors. The retained
implementation excludes every two-slot aggregate until machine spans carry a
distinct collection type. The repeated complete gate passes. This failed
prototype was never committed.

The contact constraint contains 22 stack-resident leaves. Its prologue falls
from 44 scalar load/store instructions to 22 paired transfers, reducing the
whole function from 3,692 to 3,604 bytes. Opcode tests cover general-purpose
pair loads and stores, and an encoder regression requires two pairs for a
four-leaf parameter.

The [machine-readable record](2026-09-04-spec16-arm64-aggregate-parameter-pairs.json)
contains the three exact campaigns. Each excludes one warmup and alternates
seven serial processes per binary. All series are admissible, with samples
above 20 ms and MAD below 1.75%.

| Family | Silex before | Silex after | Clang slots8 | After/before | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact normal/friction | 234.169 ms | 221.355 ms | 38.999 ms | 0.945279 | **5.6759** |
| Body integration | 1,446.737 ms | 1,440.533 ms | 49.829 ms | 0.995712 | **28.9095** |
| Constraint preparation | 3,488.801 ms | 3,547.834 ms | 228.683 ms | 1.016921 | **15.5142** |

Contact ranges are disjoint: 218.431–226.499 ms after versus
228.861–237.335 ms before. The series demonstrates a **5.472% reduction**.
Integration and preparation overlap their baselines broadly, so neither a gain
nor a regression is claimed for them.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. `zig build test -Doptimize=Debug` passes the language, unit and native
suites. The ReleaseFast optimizer gate passes 10 fixed regressions, 8 generated
native scenarios, 128 deterministic fuzz programs, 32 LLVM differential
programs and its default comparison.

This commit changes only ARM64 encoding; X64 output is unchanged. The
cumulative preceding optimizer commit still requires its exact Linux X64 and
Windows X64 native workflow. The same-layout ratios remain above 1, so Part 16
remains active and `complete-part` must not be called.
