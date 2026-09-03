# Part 16: read reuse experiment not retained

A portable-IR experiment following compiler
`8ab6a1bc45e7632feba9d1aa07f1f669827ec884` reused scalar reference reads and
immutable field projections within one block. It reduced the contact function
from 3,128 to 3,075 emitted instructions, with an unchanged 5,152-byte frame.
The experiment is **not part of the compiler candidate**.

The two small structural regressions each changed four reads/projections to
two. The qualification gate caught an initially stale field address after
whole-aggregate replacement in the interpreter. Invalidating address reuse
together with memory-read reuse corrected that case. The corrected experiment
passed check/test, optimizer-gate, compare 11 and all 176 Physics tests.
Debug and Release retained the 128 Box2D intermediate states. X64 emission
passed in both modes; native Linux/Windows execution was not performed.

The [qualified alternating campaign](2026-09-03-spec16-read-reuse-rejected.json)
nevertheless shows a slowdown:

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Before | 446.607 ms | 445.954–448.242 ms | 0.146% |
| Both transformations | 450.834 ms | 449.463–454.717 ms | 0.211% |
| Clang, same slots | 39.148 ms | 38.861–39.228 ms | 0.204% |

The before/after ranges are disjoint. Fewer emitted instructions did not
improve this workload; the remaining Silex/Clang ratio is 11.5161.

A [separate diagnostic campaign](2026-09-03-spec16-read-reuse-variants.json)
compares both transformations and each separately, always retaining field-address
reuse. Each of its six variants has one excluded warmup and seven rotating
processes; no task-owned build or other benchmark runs concurrently.

| Variant | Median | Range |
| --- | ---: | ---: |
| Before | 420.757 ms | 416.337–447.474 ms |
| Both | 426.140 ms | 420.758–451.805 ms |
| Reference reads only | 422.439 ms | 417.842–446.178 ms |
| Immutable projections only | 426.078 ms | 419.327–449.332 ms |

These overlapping ranges establish no gain for either isolated transformation.
Do not pool this diagnostic series with the preceding campaign. SIMD residence
selection also changed, but these measurements do not isolate its causal cost.

The complete proposal, exact file copies and hashes remain locally preserved
under `/private/tmp/spec16-01a06651/memory-reads-preserved/`, as recorded in the
raw report and Part checkpoint. No commit contains the rejected optimization.
The additional alias/call/loop cases in the native regression remain useful
coverage for subsequent compiler changes. Part 16 parity remains open.
