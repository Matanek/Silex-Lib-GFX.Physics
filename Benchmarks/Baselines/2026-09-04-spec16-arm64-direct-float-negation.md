# Part 16 direct ARM64 resident float negation

Compiler `feeba435c6695a9bc5bb0617d2e9c94ab2f94792` follows the direct-copy
candidate `d3a347f432e1683a5bd82f14bbe1ba83cf8de0eb`. ARM64 floating-point
negation now reads an allocated operand from its SIMD residence and writes
`FNEG` directly to the allocated result residence. Spilled endpoints retain
the ordinary stack path, and float32/float64 precision is unchanged.

An opcode regression requires resident-to-resident `FNEG` without the former
two scratch moves. Static code shrinks in every affected hot function:

| Function | Instructions | Bytes | `FMOV` | `FNEG` |
| --- | ---: | ---: | ---: | ---: |
| Contact `solve_contact` | 629 → 615 | 2,516 → 2,460 | 73 → 59 | 7 → 7 |
| `integrate_velocity` | 128 → 126 | 512 → 504 | 20 → 18 | 1 → 1 |
| `integrate_position` | 74 → 74 | 296 → 296 | unchanged | unchanged |
| Preparation `prepare` | 687 → 686 | 2,748 → 2,744 | 61 → 60 | 1 → 1 |
| Preparation function 1 | 338 → 324 | 1,352 → 1,296 | 60 → 46 | 7 → 7 |

The [machine-readable record](2026-09-04-spec16-arm64-direct-float-negation.json)
contains the exact executable hashes, correctness results and three raw
campaigns. Each campaign excludes one warmup and alternates seven serial
processes per binary. All samples exceed 20 ms and every MAD is below 0.73%.

| Family | Candidate | Previous | Clang slots8 | Candidate/previous | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact | 183.132 ms | 188.175 ms | 36.891 ms | 0.973200 | **4.9641** |
| Integration | 880.308 ms | 887.808 ms | 48.844 ms | 0.991552 | **18.0228** |
| Preparation | 2,401.394 ms | 2,408.403 ms | 214.363 ms | 0.997090 | **11.2025** |

Contact ranges are disjoint: 182.584–183.784 ms for the candidate and
187.887–189.398 ms for the previous binary. This demonstrates a **2.680%**
reduction. Integration and preparation ranges overlap, so their median changes
remain inconclusive.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. `zig build test -Doptimize=Debug` and
`zig build check -Doptimize=Debug` pass 158 language cases and all compiler,
unit and native tests. The ReleaseFast optimizer gate passes 10 fixed
regressions, 8 generated native scenarios, 128 deterministic programs, 32 LLVM
differential programs and its default comparison.

This correction changes ARM64 encoding only. The cumulative portable work
still needs its exact Linux X64 and Windows X64 native workflow. All three
same-layout ratios remain above one, so Part 16 remains active and
`complete-part` must not be called.
