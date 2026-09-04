# Part 16 ARM64 scalar reference residence

Compiler `ea38bcc` follows the aggregate-construction candidate
`5aa5858ce950fc4dbd7b3ddbad8fb0c2ca20cfd8`. Compatible ARM64 leaf-memory
functions may now keep scalar reference parameters and derived references in
the existing preserved integer register set. Direct reference loads and stores
use that resident register as their memory base instead of reloading the stack
home or copying the address through `x9`.

Collections, indices, composite operands and explicit address operations keep
their conservative stack path. Functions taking a local address or making an
unsupported call remain outside register allocation. A native regression
exercises unfused derived references and preserves exact float64 signed-zero
and NaN payload bits.

The change removes repeated pointer traffic in contact and integration:

| Function | Bytes | Instructions | Loads |
| --- | ---: | ---: | ---: |
| Contact function 0 | 3,208 → 3,136 | 802 → 784 | 141 → 114 |
| `integrate_velocity` | 1,156 → 1,056 | 289 → 264 | 100 → 73 |
| `integrate_position` | 516 → 448 | 129 → 112 | 47 → 22 |

Preparation has identical disassembly to the preceding candidate. Its
qualified same-layout ratio therefore remains 11.2726.

The [machine-readable record](2026-09-04-spec16-arm64-scalar-reference-residence.json)
contains the two exact alternating campaigns. Each excludes one warmup and
rotates seven serial processes per binary. Every timing series is admissible,
with all samples above 20 ms and MAD below 1.3%.

| Family | Silex before | Silex after | Clang slots8 | Silex/Clang |
| --- | ---: | ---: | ---: | ---: |
| Contact normal/friction | 191.313 ms | 191.736 ms | 36.875 ms | 5.1996 |
| Body integration | 1,354.058 ms | 1,279.779 ms | 48.657 ms | 26.3021 |

Contact is neutral: its before/after ranges overlap and the 0.22% median
difference is below measurement resolution. Integration's median decreases
5.486% in this campaign, though its ranges overlap at one high candidate
sample. Against the preceding qualified integration median of 1,316.934 ms,
the exact candidate is 2.821% faster.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and unchanged preparation pass their short and complete
32,768-record Box2D checks. `zig build test -Doptimize=Debug` passes 158
language cases and all compiler, unit and native tests. The ReleaseFast
optimizer gate passes 10 fixed regressions, 8 generated native scenarios, 128
deterministic programs, 32 LLVM differential programs and its default
comparison.

This commit changes only ARM64 allocation and encoding; X64 output is
unchanged. The cumulative portable optimizer work still needs its exact Linux
X64 and Windows X64 native workflow. The same-layout ratios remain above one,
so Part 16 remains active and `complete-part` must not be called.
