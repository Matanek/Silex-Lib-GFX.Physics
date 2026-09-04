# Part 16 ARM64 view state residence across direct calls

Compiler `0599905ac3c2f5998afdb5259eafe4672aeb0892` follows the flat
aggregate-flow candidate `5b2f3eab622a4e26cf3bf913a577686d4b3e0f80`. Direct Silex calls now
use callee-saved ARM64 colors. Stable view descriptors and their loop indices
can consequently remain resident across a call, while checked failures retain
the original index and diagnostic. Addressed spans remain pinned and form copy
affinity barriers, preserving snapshots across indirect mutation.

The integration driver falls from 3,843 to 225 instructions. The contact solver
falls from 591 to 579; the preparation path is statically unchanged. The
[machine-readable record](2026-09-04-spec16-arm64-view-call-residence.json)
contains the three exact alternating campaigns and portability evidence.

| Family | Silex before | Silex after | Clang slots8 | Reduction | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact normal/friction | 166.565 ms | 102.940 ms | 37.636 ms | 38.198% | **2.7351** |
| Body integration | 252.705 ms | 150.511 ms | 49.855 ms | 40.440% | **3.0190** |
| Constraint preparation | 1,654.924 ms | 1,650.129 ms | 228.954 ms | inconclusive | **7.2073** |

Contact and integration have disjoint before/after ranges. Preparation overlaps
and no gain is claimed. Every series is admissible with MAD below 1.54%.
Contact passes 1,280 scalar comparisons with maximum error 6.4e-7. Integration
and preparation pass their short and complete 32,768-record Box2D checks; the
known independent integration trajectory diagnostic remains outside its initial
budget because of the separately documented legal FMA contraction difference.

Debug check/test, the complete ReleaseFast optimizer gate, compare 11 and all
176 Physics tests pass. Workflow
[`33871338995`](https://github.com/Matanek/Silex/actions/runs/33871338995)
executes the exact SHA successfully on Linux X64 and Windows X64. The cumulative
ratios remain above 1, so Part 16 stays active.
