# Part 16: unused checked aggregate payloads

Compiler `4183a600a17a2cdbbce25cf33b5c5d37a2684537` follows
`8ab6a1bc45e7632feba9d1aa07f1f669827ec884`. The rejected read-reuse experiment
is absent. In compatible ARM64 Release functions, a checked dynamic collection
read with an unused aggregate result retains its bounds checks and diagnostics
while omitting the payload copy. Both views and owning lists keep negative
indexing. Debug and functions using recycled stack slots retain their lowering.

The structural regression fails before and passes after the change. Native
execution covers valid indices 0 and -1 and invalid indices 2 and -3 in a
two-element view and list. The expected failure diagnostics appear in the test
logs; the tests and build commands exit successfully. The existing native
aggregate fixture also gains alias/call/loop coverage.

The contact function retains its 5,152-byte frame and its arithmetic/SIMD
operations. It emits 2,924 instructions instead of 3,128: 84 payload loads,
84 payload stores and 36 associated address instructions are removed.
These total function sizes include cold diagnostic paths.

The [alternating campaign](2026-09-03-spec16-dead-loads.json) records one excluded
warmup and seven rotating processes per variant, without concurrent task-owned
builds, tests or benchmarks:

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 424.588 ms | 420.942–447.520 ms | 0.859% |
| Silex after | 340.192 ms | 338.073–359.853 ms | 0.623% |
| Clang, same slots | 37.473 ms | 37.310–39.144 ms | 0.435% |
| Clang, packed | 37.110 ms | 36.913–39.070 ms | 0.531% |

The disjoint ranges demonstrate a **19.877% reduction** on this kernel. The
remaining Silex/Clang ratio is 9.0783, so compiler parity still fails.
All 128 intermediate Box2D states pass in both native modes with the unchanged
6.4e-7 maximum absolute error. Layouts, precision, FMA policy, Clang flags and
the pinned oracle revision are unchanged from the preceding qualifications.

Check/test in Debug, optimizer-gate and optimizer-oracle compare 11 pass.
All 176 Physics tests pass. The correction scene and dense Release corpus pass;
every non-timing dense observation matches Part 15. That single dense run is
a correctness check, not a speedup claim. Linux/Windows emit the enriched
aggregate fixture in both modes; their native execution remains pending for
the earlier portable changes.

The timed artifact was first emitted with a Debug build of the compiler. A
ReleaseFast compiler build reproduces its complete SHA-256 when using the same
output basename. The raw report records both provenance and binary hashes.
Preparation, integration and the Part 16 parity gate remain open.
