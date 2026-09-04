# Part 16 direct ARM64 aggregate returns

Compiler `de15327b54fd6f8d9efa2dd63836dcbb92acdaae` follows the view-call
residence candidate `0599905ac3c2f5998afdb5259eafe4672aeb0892`. An aggregate
constructed immediately before its return is now written straight into the
caller's hidden result storage. Ordinary slot-width collection replacements
form their stack source address once and use paired `LDP`/`STP` transfers.
Control-flow entry points, compact float32 collections and replacements wider
than 64 slots retain their established paths.

In the preparation witness, `prepare` falls from 304 to 252 instructions, its
helper from 321 to 273, and the driver from 3,750 to 3,725. The
[machine-readable record](2026-09-04-spec16-arm64-direct-aggregate-returns.json)
contains the exact alternating campaign and executable hashes.

| Family | Silex before | Silex after | Clang slots8 | Reduction | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Constraint preparation | 1,682.906 ms | 1,577.107 ms | 229.740 ms | **6.287%** | **6.8647** |

The before/after ranges are disjoint: 1,633.758–1,698.973 ms before versus
1,543.262–1,609.206 ms after. All series are admissible; the largest MAD is
1.819%. Short and complete preparation checks pass all 32,768 records and
851,968 fields against Box2D, with maximum Silex error 2.2e-7.

Debug check/test, the complete ReleaseFast optimizer gate, compare 11 and all
176 Physics tests pass. A broader regional allocation experiment reduced code
size but crashed during validation; it was removed completely and is absent
from this commit. With the current contact and integration campaigns inherited
from `0599905`, the cumulative ratios are contact **2.7351**, integration
**3.0190** and preparation **6.8647**. Part 16 therefore remains active.
