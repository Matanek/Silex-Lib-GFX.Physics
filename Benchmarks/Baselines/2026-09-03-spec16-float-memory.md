# Part 16: direct floating-point memory transfers

Compiler `8ab6a1bc45e7632feba9d1aa07f1f669827ec884` follows
`fe3c3f7b58e98a6fb428b3b4a2ca19e78caf5467`. ARM64 reference loads and stores
use the floating-point register bank directly when the value resides there.
64-bit floating-point stack transfers also avoid an intermediate integer
register, in both stack-address windows and in Debug and Release. Every
memory access retains its previous width; no arithmetic is changed.

Two structural native regressions fail before and pass after the change.
They also execute exact signed-zero and quiet/signaling-NaN payload checks,
including stack slots on either side of the second address window.
The instruction encoding tests cover the scaled-address limits. The focused
suite passes 278 tests. All temporary probes were removed before committing.

The contact function retains its 5,152-byte frame. It emits 3,128 instructions
instead of 3,203, removing 75 integer/floating-point transfers. These totals
include cold diagnostic paths and do not represent executed instruction counts.
The [raw alternating campaign](2026-09-03-spec16-float-memory.json) records:

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 441.943 ms | 439.243–464.144 ms | 0.611% |
| Silex after | 430.384 ms | 422.569–448.513 ms | 0.884% |
| Clang, same slots | 37.983 ms | 37.152–39.346 ms | 2.188% |
| Clang, packed | 36.881 ms | 36.496–38.838 ms | 0.965% |

One excluded warmup precedes seven rotating processes per variant. No other
task-owned build, test or benchmark runs during measurement. The before/after
ranges overlap, so **the speedup is inconclusive**. The remaining Silex/Clang
ratio is 11.3310: compiler parity still fails. The workload, layouts, Clang
flags and pinned Box2D revision match the preceding qualifications.

`zig build check -Doptimize=Debug`, `zig build test -Doptimize=Debug`,
`zig build optimizer-gate` and `zig build optimizer-oracle -- compare 11`
pass. All 176 Physics tests pass. Both native modes match all 128 intermediate
Box2D states with maximum absolute error 6.4e-7. The correction scene and a
dense Release corpus execution pass; all non-timing dense observations match
Part 15 exactly. That single run is a correctness check, not a speedup claim.

This change touches only ARM64 machine emission. Native Linux/Windows execution
of the earlier portable optimizer changes remains pending. Preparation,
integration and the overall Part 16 parity gate remain open.
