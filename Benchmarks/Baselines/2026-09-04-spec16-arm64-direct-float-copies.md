# Part 16 direct ARM64 resident float copies

Compiler `d3a347f432e1683a5bd82f14bbe1ba83cf8de0eb` follows the
dominating-view candidate `05df115c6b9c0f634a3799bbf8a960762c9274a7`.
ARM64 copies now load a stack-resident floating-point value directly into its
assigned SIMD destination, or store directly from its resident SIMD source.
The existing lane and scratch paths remain available when neither endpoint has
a scalar residence. The operation remains an exact 64-bit payload transfer.

Opcode regressions require both direct directions and reject the former
scratch `FMOV`. Static code shrinks without adding loads or stores:

| Function | Instructions | Bytes | `FMOV` |
| --- | ---: | ---: | ---: |
| Contact `solve_contact` | 655 → 629 | 2,620 → 2,516 | 99 → 73 |
| `integrate_velocity` | 128 → 128 | 512 → 512 | unchanged |
| `integrate_position` | 74 → 74 | 296 → 296 | unchanged |
| Preparation `prepare` | 723 → 687 | 2,892 → 2,748 | 97 → 61 |
| Preparation function 1 | 362 → 338 | 1,448 → 1,352 | 84 → 60 |

The [machine-readable record](2026-09-04-spec16-arm64-direct-float-copies.json)
contains the exact executable hashes, correctness results and raw campaigns.
Every campaign excludes one warmup and alternates seven serial processes per
binary. All samples exceed 20 ms and every MAD remains below 1.18%.

| Family | Candidate | Previous | Clang slots8 | Candidate/previous | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact | 187.930 ms | 188.852 ms | 36.793 ms | 0.995118 | **5.1078** |
| Integration | 886.448 ms | 884.343 ms | 47.472 ms | 1.002380 | **18.6731** |
| Preparation confirmation | 2,416.752 ms | 2,391.587 ms | 214.179 ms | 1.010523 | **11.2838** |

Contact and integration ranges overlap, so neither timing change is claimed.
The first preparation campaign showed a narrow disjoint increase: its
candidate minimum was 2,396.846 ms and the previous maximum 2,396.531 ms. A
second independent campaign was required; its ranges overlap broadly at
2,396.456–2,442.784 ms and 2,383.974–2,442.871 ms. The initial slowdown did
not reproduce, and no preparation timing change is claimed.

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
