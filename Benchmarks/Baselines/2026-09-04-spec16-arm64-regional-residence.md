# Part 16 regional ARM64 scalar residence

Compiler `55d5cdbf3e02afdb9db9d593971c15c9269f24ac` follows the direct
aggregate-return candidate
`de15327b54fd6f8d9efa2dd63836dcbb92acdaae`. ARM64 register allocation
can now color a profitable scalar floating-point region inside a function
that also contains unsupported operations. Unsupported instructions are hard
liveness barriers: their complete operands and results, together with every
interval live across them, stay on the stack. Mixed aggregate loads and
aggregate calls inside loops retain the whole-function spill path.

The preparation kernel is the witness selected by the profitability gate. Its
alternating campaign falls from 1,610.820 ms to 539.932 ms, a **66.481%**
reduction. The before and after ranges are disjoint: 1,547.243–1,634.379 ms
before versus 530.471–543.277 ms after. The largest MAD in the campaign is
0.524%.

| Family | Silex | Clang slots8 | Silex/Clang | Initial Part 16 ratio |
| --- | ---: | ---: | ---: | ---: |
| Contact | 105.611 ms | 38.650 ms | **2.7325** | 4.9641 |
| Integration | 154.154 ms | 51.143 ms | **3.0142** | 18.0228 |
| Preparation | 539.932 ms | 234.780 ms | **2.2997** | 11.2025 |

All three campaigns use one excluded warm-up and seven alternating serial
processes. Contact short validation, integration full validation and
preparation full validation pass against the pinned Box2D oracles. Debug
check/test, the complete ReleaseFast optimizer gate, `compare 11`, and all
176 Physics tests pass. The
[machine-readable record](2026-09-04-spec16-arm64-regional-residence.json)
contains every sample and executable hash.

The three parity ratios remain above 1.0, so Part 16 remains active.
