# Part 16 direct indexed mutable references

Compiler `2fa1b0dd10f114ab5b78f0d51744786ebcad5cdc` follows the direct
resident-negation candidate `feeba435c6695a9bc5bb0617d2e9c94ab2f94792`.
An indexed value passed to a mutable parameter now uses the element's direct
reference when its collection root is stable. The compiler no longer copies
an entire aggregate into a temporary and writes the whole value back after the
call. Owning-list detachment, negative view indices and every unproved bounds
diagnostic remain intact.

Release also removes a dead type-checking snapshot when the same direct
reference performs its check, and extends counted-loop bounds proofs to
mutable element references from the same unchanged view local. The regression
requires a counted mutable-view loop to contain one bounded collection
reference, with no collection load or collection replacement.

Static native code shrinks most strongly in the integration driver:

| Function | Instructions | Bytes |
| --- | ---: | ---: |
| Contact `solve_contact` | 615 → 591 | 2,460 → 2,364 |
| `integrate_velocity` | 126 → 126 | 504 → 504 |
| `integrate_position` | 74 → 53 | 296 → 212 |
| Integration driver | 1,822 → 293 | 7,288 → 1,172 |
| Preparation `prepare` | 686 → 639 | 2,744 → 2,556 |
| Preparation function 1 | 324 → 324 | 1,296 → 1,296 |

The [machine-readable record](2026-09-04-spec16-direct-indexed-mutable-references.json)
contains exact executable hashes, correctness results and the three raw
campaigns. Each campaign excludes one warmup and alternates seven serial
processes per binary.

| Family | Candidate | Previous | Clang slots8 | Change | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact | 167.072 ms | 196.070 ms | 39.135 ms | **−14.790%** | **4.2691** |
| Integration | 255.368 ms | 945.373 ms | 49.691 ms | **−72.988%** | **5.1391** |
| Preparation | 2,440.859 ms | 2,594.158 ms | 229.678 ms | −5.910% | **10.6273** |

Contact and integration before/after ranges are disjoint, so both reductions
are demonstrated. Preparation ranges overlap; its median movement remains
inconclusive despite the smaller static `prepare` function.

All 1,280 contact scalar comparisons pass with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. `zig build test -Doptimize=Debug` passes 158 language cases and 1,138
compiler, unit and native tests. `zig build check -Doptimize=Debug` and the full
ReleaseFast optimizer gate pass, including 10 fixed regressions, 8 generated
native scenarios, 128 deterministic programs, 32 LLVM differential programs
and the default comparison.

This is the first correction that removes the integration factor of eighteen,
but no same-layout family has reached parity. The cumulative exact Linux X64
and Windows X64 workflow also remains pending, so Part 16 stays active and
`complete-part` must not be called.
