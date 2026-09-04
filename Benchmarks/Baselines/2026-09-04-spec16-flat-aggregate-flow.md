# Part 16 flat aggregate value flow and ARM64 parameter safety

Compiler `5b2f3eab622a4e26cf3bf913a577686d4b3e0f80` follows
`2fa1b0dd10f114ab5b78f0d51744786ebcad5cdc`. Release now splits
unaddressed flat numeric and boolean aggregate locals into scalar field locals.
It reconstructs a value at its original observation point and omits fields
unchanged from the current same-block snapshot. Direct calls can also borrow a
single-use collection element when the callee only projects fields and every
call site keeps the address stable. Scalar deep copies become aliases.

Large view snapshots with more than eight scalar fields are projected through
field references even after their bounds have been proven. Their bounded state
is preserved, so the transformation adds no check. Small bounded aggregates
keep their compact native copy and SIMD seed; the optimizer portal's Boids
contract requires this distinction on both ARM64 and X64. An unused checked
snapshot is also removed when the same later indexed replacement covers its
check without an intervening effect.

The full Physics validation exposed a pre-existing ARM64 regression in commit
`50084429478dff29d9f490e6a6aeca2e20335a3b`. A stack-passed aggregate after
eight parameters uses `x10` for its incoming pointer. The first paired load also
used `x10` as its second destination and destroyed that pointer before the next
pair. LLDB stopped in `silex_function_161` on the resulting
`LDP x9, x10, [x10, #16]`. Paired transfers now use `x11` as their second
scratch and exclude leaves with a scalar register residence. Dedicated encoder
tests cover the stack-passed multi-pair case and resident leaves. The targeted
BodyControl test and all Physics tests pass afterward.

## Static ARM64 effect

Instruction counts come from adjacent `_silex_function_N` symbol addresses in
the exact Mach-O candidates:

| Case | Function | Before | After |
|---|---:|---:|---:|
| contact | hot solver | 591 | 591 |
| contact | driver | 6,560 | 5,367 |
| integration | velocity | 126 | 126 |
| integration | position | 53 | 53 |
| integration | driver | 4,822 | 3,843 |
| preparation | `prepare` | 639 | 304 |
| preparation | helper | 324 | 321 |
| preparation | driver | 4,921 | 3,750 |

The preparation constructor therefore loses 335 instructions and its driver
loses 1,171. Contact and integration keep their hot arithmetic functions; the
smaller drivers do not produce a separately demonstrated timing gain.

## Correctness and qualified campaigns

The candidates were compiled in Release with `--nocache`. Contact checks all
128 records and 1,280 scalars against Box2D, with a maximum Silex error of
`6.4e-7`. Integration and preparation pass both short and complete checks;
their complete campaigns cover 32,768 records. Each timing excludes one warmup
and alternates seven fresh processes across the candidate, its predecessor,
Clang slots8 and Clang packed4. Every MAD is below 2.37%.

| Case | Silex median | Previous Silex | Clang slots8 | Silex/Clang | Result |
|---|---:|---:|---:|---:|---|
| contact | 162.319 ms | 168.135 ms | 39.154 ms | **4.1457** | parity missed; before/after ranges overlap |
| integration | 254.470 ms | 254.095 ms | 50.175 ms | **5.0716** | parity missed; before/after ranges overlap |
| preparation | 1,618.156 ms | 2,433.785 ms | 224.449 ms | **7.2095** | parity missed; **33.513% reduction**, disjoint ranges |

Exact candidate SHA-256 values:

- contact: `994549901639cf5e7973895b7c6475728d979a59696a2c3a8ff2f1f229af4d40`;
- integration: `dccc396249b696a2dca3df5962b21114cfb34112f3835293a245cb5a84f122e5`;
- preparation: `43430099306e31a37a57b590d73a736fa6e29f4ed5b69f53468a5790e29963d5`.

The complete samples, executable paths, oracle hashes, workload metadata,
numerical budgets and comparisons are in the adjacent JSON report.

## Gates and remaining limit

`zig build test -Doptimize=Debug` and `zig build check -Doptimize=Debug`
pass 158 language cases and all compiler, unit and native tests. The
ReleaseFast optimizer gate passes 10 fixed regressions, 8 generated native
scenarios, 128 deterministic programs, 32 LLVM differential programs and its
default comparison. The exact ReleaseFast compiler passes all 176 Physics tests
in 28 files.

All three same-layout ratios remain above one. This commit also changes ARM64
code generation after the last cumulative Linux X64 and Windows X64 run, so
native portability must be repeated on this exact HEAD before Part 16 can
finish. No parity or completion is claimed.
