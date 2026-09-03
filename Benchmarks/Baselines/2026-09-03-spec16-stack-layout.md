# Part 16: storage for eliminated values

Compiler `fe3c3f7b58e98a6fb428b3b4a2ca19e78caf5467` follows the scalar-memory
candidate `d8f37f3bab4a37572d781bc9c796dbea79096c2f`. Native layout retains
storage only for value IDs occurring in definitions, uses, parameters or
captures. It keeps stable IR IDs and the complete ABI parameter list.

Two structural regressions fail before and pass after the correction. An IR
function with 256 value declarations but only an unused parameter, an unused
capture and a returned constant needs three slots. A branch fixture with
thousands of removed declarations no longer enters the fallback that reuses
stack slots; its live values retain distinct ordinary homes.

The contact function's emitted stack frame falls from 6,656 to 5,152 bytes
(22.60%). Its 3,203 instructions are unchanged in count. The
[alternating campaign](2026-09-03-spec16-stack-layout.json) therefore records
the timing separately from that structural improvement:

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 461.938 ms | 441.542–463.263 ms | 0.287% |
| Silex after | 461.111 ms | 439.560–463.421 ms | 0.166% |
| Clang, same slots | 38.967 ms | 36.871–39.280 ms | 0.803% |
| Clang, packed | 38.762 ms | 36.509–39.114 ms | 0.222% |

There is one excluded warmup and seven rotating processes per variant, with
no concurrent task-owned build or benchmark. The ranges overlap: **no speedup
is demonstrated**. The remaining Clang ratio is 11.8334, so parity still fails.
All 128 intermediate states retain the prior 6.4e-7 Silex maximum error.

`zig build check -Doptimize=Debug`, `zig build test -Doptimize=Debug`,
`zig build optimizer-gate`, and `zig build optimizer-oracle -- compare 11`
pass. This includes the native Debug/Release/interpreter aggregate regression.
All 176 Physics tests pass again. The Release correction scene and a single
dense corpus execution pass; every non-timing dense field exactly matches the
Part 15 observation. That execution is a correctness check, not a timing series.
The aggregate witness is emitted for Linux X64 and Windows X64 in both modes;
native execution on those systems is still pending.

The contact workload, Clang flags, precision, storage and pinned Box2D revision
are the same as the [preceding qualification](2026-09-03-spec16-scalar-memory.md).
Preparation and integration witnesses and the Part 16 parity gate remain open.
