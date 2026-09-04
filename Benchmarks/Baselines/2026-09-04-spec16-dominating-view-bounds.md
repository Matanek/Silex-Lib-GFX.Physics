# Part 16 dominating mutable-view bounds proof

Compiler `05df115` follows the resident-float candidate `d1c446c`. Release now
uses a checked mutable-view reference in the entry block as a bounds proof for
an equivalent reference in a later block. Equivalence is limited to unchanged
view descriptors and indices reached through copies, invariant locals, or
fields of value structures. Calls, storage-replacing mutations, explicit local
addresses and synchronization disable the proof.

The later reference remains local to its use, so register allocation does not
extend an address lifetime across the control-flow graph. ARM64 and X64 still
load the current view descriptor and normalize negative indices; they omit only
the duplicate comparisons, failure branches and diagnostic body. The first
checked reference retains the original source diagnostic and rejects an invalid
index before any bounded reference can execute.

For contact `solve_contact`, the two checked snapshot references prove the two
matching destination references at the final writes:

| Static measure | Before | After |
| --- | ---: | ---: |
| Bytes | 3,116 | 2,620 |
| Instructions | 779 | 655 |
| Loads | 114 | 112 |
| Stores | 39 | 39 |
| Branches | 81 | 67 |
| `svc` instructions in cold diagnostics | 12 | 6 |
| Checked view references | 4 | 2 |

Integration and preparation disassemblies are unchanged. The
[machine-readable record](2026-09-04-spec16-dominating-view-bounds.json)
contains the exact campaign, executable hashes, validation and inherited ratios.

After one excluded warmup, the campaign alternates seven serial processes per
binary. Every sample exceeds 20 ms and all MAD values are below 0.17%.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex candidate | 188.668 ms | 188.163–188.970 ms | 0.160% |
| Silex before | 191.476 ms | 191.252–191.963 ms | 0.108% |
| Clang slots8 | 36.781 ms | 36.724–37.900 ms | 0.139% |
| Clang packed4 | 36.534 ms | 36.512–36.886 ms | 0.060% |

The Silex ranges are disjoint. The median decreases by **1.467%** and the
same-layout Silex/Clang ratio becomes **5.1295**. The strict parity gate remains
`missed`.

All 1,280 contact scalar comparisons pass against the actual Box2D adapter;
the maximum Silex error remains 6.4e-7. `zig build test -Doptimize=Debug` and
`zig build check -Doptimize=Debug` pass 158 language cases plus all compiler,
unit and native tests. The ReleaseFast optimizer gate passes 10 fixed
regressions, 8 generated native scenarios, 128 deterministic programs, 32 LLVM
differential programs and its default comparison.

The portable proof and both verified native encoders changed. Exact Linux X64
and Windows X64 execution remains required for the cumulative candidate. The
current ratios are contact **5.1295**, integration **18.1064** and preparation
**11.1240**. All remain above one, so Part 16 stays active and `complete-part`
must not be called.
