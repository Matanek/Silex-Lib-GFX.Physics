# Part 16 mutable-view reference and bounds-check reuse

Compiler `00aac59ef4aa0221cbec807ee164740ae802ddfc` follows the fully
portable scalar-min/max candidate `e5907b4a1816fa6721133afadecb5c0563b5bede`.
In call-free dense blocks, Release now keeps non-escaping mutable-view
descriptors, immutable aggregate field projections and identical element
references across scalar reference stores. An unused checked aggregate
snapshot disappears only when an effectful reference proves the same
collection and index without moving the observable bounds failure across a
store or call.

The structural regression writes three fields on each of two view elements.
It requires two checked element references instead of six and no dead checked
snapshot. Interpreter and native results agree; direct ARM64 execution also
checks the valid negative index `-1` and retains a runtime failure for `-3`.
The existing aggregate, alias, class-owned collection and mutable-lane
regressions remain green.

The three raw campaigns in the
[machine-readable record](2026-09-04-spec16-mutable-view-reference-reuse.json)
exclude one warmup and alternate seven serial processes per binary. Every
series is admissible: all samples exceed 20 ms and all MAD values are below
1.01%. The Silex-before binary is the exact retained `e5907b4` contact,
integration or preparation witness; the Clang and Box2D binaries are unchanged.

| Family | Silex before | Silex after | Clang slots8 | After/before | Silex/Clang |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact normal/friction | 290.448 ms | 224.655 ms | 37.710 ms | 0.773478 | **5.9574** |
| Body integration | 1,426.718 ms | 1,430.113 ms | 49.487 ms | 1.002379 | **28.8988** |
| Constraint preparation | 3,484.448 ms | 3,494.957 ms | 214.529 ms | 1.003016 | **16.2913** |

The contact ranges are disjoint: 222.376–227.804 ms after versus
289.227–297.252 ms before. This demonstrates a **22.652% reduction** for the
targeted kernel. Integration and preparation ranges overlap their baselines;
no gain or regression is claimed for those two families.

The contact comparator passes all 1,280 scalar comparisons with maximum Silex
error 6.4e-7. Integration and preparation pass both short and 32,768-record
full checks; the integration report retains its explicit independent
accumulated-trajectory distinction while replaying every transition from
identical inputs. `zig build test -Doptimize=Debug` passes the language, unit
and native suites. The ReleaseFast optimizer gate passes 10 fixed regressions,
8 generated native scenarios, 128 deterministic fuzz programs, 32 LLVM
differential programs and the default 11-sample comparison.

Two additional experiments were rejected before this candidate. Removing
aggregate-parameter residence modestly helped one integration observation but
regressed contact and did not move preparation. Raising large void inlining
regressed contact and integration without a preparation benefit. Their patches
remain under `/private/tmp/spec16-01a06651`; neither is committed.

The candidate is locally validated on macOS ARM64. Its exact Linux X64 and
Windows X64 native workflow is still pending, so this report is a local
candidate record rather than a portability qualification. All three
same-layout ratios remain above the required ceiling of 1. Part 16 remains
active and no cumulative `complete-part` candidate may be registered yet.
