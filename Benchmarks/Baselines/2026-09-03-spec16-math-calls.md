# ARM64 residences across scalar math calls

Compiler `743ee2287646fc193047c89a2897e92304fe225a` follows
`4183a600a17a2cdbbce25cf33b5c5d37a2684537`. Functions containing exact scalar
system-math calls can retain values in ABI-preserved ARM64 registers.
Arguments/results keep their stack homes and every actual C call remains.
No math intrinsic, approximation, reassociation or errno policy is introduced.
Unknown providers/signatures retain the conservative path; call-free allocation
keeps its existing register set.

The structural regression fails before and passes after for float32/64 and both
stack windows. A native fixture verifies live loop values and exact NaN and
signed-zero payloads through linked libSystem calls. The fixture is wired into
check/test on a macOS ARM64 host and has its own `test-native-math-calls` gate.
Both Debug and Release pass; its arithmetic subset also passes the interpreter.
Raw-address bit inspection remains native-only.

The [alternating campaign](2026-09-03-spec16-math-calls.json) uses the unchanged
integration witness, macOS 26.6.2, Apple M3 Pro, native Release. One excluded
warmup precedes seven processes per variant in rotating order; no task-owned
build or test runs concurrently. Clang keeps `-O3 -DNDEBUG -ffp-contract=fast`.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex before | 2,134.442 ms | 2,131.029–2,168.575 ms | 0.149% |
| Silex after | 1,430.181 ms | 1,425.754–1,441.860 ms | 0.310% |
| Clang, slots8 | 48.053 ms | 46.721–50.004 ms | 2.156% |
| Clang, packed | 45.377 ms | 44.805–47.349 ms | 1.261% |

The disjoint ranges demonstrate a **32.995% reduction** for this integration
case. The observed after/before ratio range is 0.65746–0.67660. Silex/Clang
remains **29.7626**, so parity still fails.

All 32,768 printed integration states are byte-for-byte identical before/after.
The original independent-trajectory FMA diagnostic is therefore unchanged;
every replayed transition still passes. Contact and preparation executables
recompiled with their original basenames have exactly their preceding hashes.
Their previous ratios, 9.0783 and 25.1739, remain applicable; no duplicate timing
campaign is claimed for those unchanged binaries.

Check/test Debug, the linked native gate, optimizer-gate and compare 11 pass.
All 176 Physics tests pass. The correction scene and dense Release corpus pass;
every non-timing dense field matches Part 15 exactly. The dense run is a
correctness check, not evidence of an engine speedup. X64 allocation is unchanged
by this ARM64 slice. Native Linux/Windows execution for earlier portable changes
remains pending; no remote workflow has run.
