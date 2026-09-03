# Body integration compiler witness

Compiler `4183a600a17a2cdbbce25cf33b5c5d37a2684537`, native Release,
macOS 26.6.2 ARM64 on Apple M3 Pro. Production Physics is unchanged.
The [protocol and mapping](../Oracle2D/StageKernels.md) specify the equivalent
Silex/C velocity/position integration and the actual pinned Box2D reference.

The [raw campaign](2026-09-03-spec16-integration.json) contains one excluded
warmup and seven serial processes in rotating order. Each timed process
integrates 8,192 bodies for 2,048 passes. No task-owned build or test ran
concurrently. Apple Clang uses `-O3 -DNDEBUG -ffp-contract=fast`; SIMD remains
available and neither layout uses forced inlining or fast-math.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex, slots8 | 2,134.324 ms | 2,130.163–2,155.221 ms | 0.174% |
| Clang, slots8 | 47.098 ms | 46.677–47.566 ms | 0.586% |
| Clang, packed | 45.321 ms | 44.459–47.180 ms | 1.560% |

Timing is admissible. The matching-layout ratio is **45.3167** and parity
fails. The two Clang layout ranges overlap; no layout gain is established.
This larger gap is independent of contact resolution. It does not attribute
the cost of production Physics or establish a regression from an older compiler.

Debug and Release pass the eight-step trace and all 32,768 replayed transitions
from identical inputs through Box2D. The maximum local Silex error in the long
replay is 1.14e-5; all capped flags match exactly. Timed signatures match the
verified final states. Fifteen contact/stage comparator tests pass, including
missing/duplicate/non-finite records, every output field, incorrect timing
metadata and a local transition that must not use the cumulative allowance.

The independent long trajectories are **not equal within the initial diagnostic
budget**: maximum Silex/Box2D difference is 0.0084341, versus 1.53e-5 for Clang.
The reduced damping case and native instructions identify different legal FMA
contractions and accumulated rotation phase error. The initial budget remains
unchanged and its failure remains in the raw data. The stronger per-transition
replay qualifies local operations; it does not convert that diagnostic into a
claim of long-term orientation agreement. No timing or native-execution claim
is made for X64. Preparation coverage and overall compiler parity remain open.
