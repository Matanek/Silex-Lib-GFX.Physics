# Part 16 scalar min/max native portability

The manually dispatched [native-portability run 33813586089](https://github.com/Matanek/Silex/actions/runs/33813586089)
passed on Linux X64 and Windows X64 at exact compiler commit
`e5907b4a1816fa6721133afadecb5c0563b5bede`. Both jobs checked out the pinned
STD fixture dependency at `5a018305fb470dfe00e94466150b3c04f207e252`, built
Silex with Zig 0.16.0, then compiled and executed `ScalarMathMinMax.sx` in
native Debug and Release. The fixture checks float32 and float64 min/max NaN
selection and signed zero, plus all six comparisons with unordered operands.

| Target | Runner | Job | Result |
| --- | --- | --- | --- |
| Linux X64 | ubuntu-24.04 | 100840694865 | Passed |
| Windows X64 | windows-2025 | 100840694926 | Passed |

The final run followed two useful failed attempts. Run
[`33810121895`](https://github.com/Matanek/Silex/actions/runs/33810121895) at
`dcbdcef` stopped before the new fixture because STD was absent from the
standalone workflow checkout. Commit `38dc99c` added the immutable STD checkout
and workspace link. Run
[`33812339053`](https://github.com/Matanek/Silex/actions/runs/33812339053) then
reached the fixture and failed its first unordered X64 predicate on both
platforms. Commit `e5907b4` corrected the general X64 float-comparison lowering:
ordered predicates now exclude parity and `!=` includes it. Structural tests
cover all six predicates, and the expanded fixture prevents this regression.

Local validation at the final SHA also passed `zig build test`, `zig build
check`, the dedicated Silex tests, macOS ARM64 native Debug/Release, and Linux
and Windows X64 cross-emission in both modes. The workflow source, compiler
sources, job metadata and retained-log hashes are recorded in the
[machine-readable evidence](2026-09-04-spec16-minmax-native-portability.json).

Only the named Silex branch was pushed. No tag, release, default-branch update
or Physics push occurred. This establishes native portability for the scalar
min/max candidate; it is not a timing campaign. The same-layout ratios remain
7.5998 for contact, 30.4481 for integration and 16.0049 for preparation, all
above the required ceiling of 1. Part 16 remains active.
