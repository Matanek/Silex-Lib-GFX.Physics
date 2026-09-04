# Part 16 ARM64 aggregate construction affinity

Compiler `5aa5858ce950fc4dbd7b3ddbad8fb0c2ca20cfd8` follows the ARM64
reference-field candidate `75628fadba8c89c03e65c36d13fa7023fc834813`.
The ARM64 register allocator now treats every used leaf produced by a complete
`aggregate_init` as a copy-affinity edge to its source leaf. Existing liveness
and source-redefinition checks decide whether both values may share a register.

The retained scope requires every leaf of the constructed aggregate to have a
use. An initial broader prototype changed the established residence chosen for
a live/dead sibling pair and failed its unit regression. The narrowed form
leaves the entire constructor on the prior path when any result leaf is dead.
The full suite and native sibling regression then pass. No failed form is
committed.

Preparation benefits because successive complete reconstructions of
`Prepared` can keep unchanged fields in their existing registers:

| Static measure in `prepare` | Before | After |
| --- | ---: | ---: |
| Function size | 5,768 B | 2,960 B |
| `fmov` | 440 | 104 |
| Loads | 428 | 239 |
| Stores | 367 | 190 |

The complete contact and integration disassemblies are unchanged from the
preceding candidate. Their qualified same-layout ratios therefore remain
5.1743 and 27.0362.

The [machine-readable record](2026-09-04-spec16-arm64-aggregate-construction-affinity.json)
contains the exact preparation campaign. It excludes one warmup and alternates
seven serial processes per binary. The timing is admissible: every sample is
above 20 ms and every MAD is below 5%.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex after | 2,472.506 ms | 2,386.858–2,523.919 ms | 2.079% |
| Silex before | 3,015.105 ms | 2,980.334–3,098.517 ms | 0.246% |
| Clang slots8 | 219.337 ms | 214.377–228.718 ms | 2.261% |
| Clang packed4 | 157.884 ms | 157.180–166.401 ms | 0.364% |

The before/after ranges are disjoint. Aggregate construction affinity reduces
preparation by **17.996%** and leaves a same-layout ratio of **11.2726**.

The short and complete 32,768-record preparation comparisons pass against
Box2D. `zig build test -Doptimize=Debug` passes 158 language cases and all
1,130 compiler, unit and native tests. The ReleaseFast optimizer gate passes
10 fixed regressions, 8 generated native scenarios, 128 deterministic
programs, 32 LLVM differential programs and its default comparison.

This commit changes only ARM64 allocation; X64 output is unchanged. The
cumulative preceding portable optimizer commit still needs its exact Linux X64
and Windows X64 native workflow. The cumulative ratios remain contact 5.1743,
integration 27.0362 and preparation 11.2726, all above one. Part 16 remains
active and `complete-part` must not be called.
