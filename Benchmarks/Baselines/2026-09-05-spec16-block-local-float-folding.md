# Part 16 block-local finite float folding

Compiler `d91342aaf02e4c15fab8296135d63f1fe0aa53cd` follows the
multiplatform integration merge `042c70a`. Release optimization now folds
direct float32 and float64 constants inside every basic block, including
functions with branches. It accepts finite add, subtract, multiply, divide
and comparisons; division by zero, non-finite operands or results, and
unsupported operations remain explicit. Constants are cleared at each block,
so the change performs no alias, local, dominance or join propagation.

The integration witness previously recomputed constants such as `1 / 240` and
the angular-speed limit on every call. The candidate removes those runtime
operations. Its executable remains 101,368 bytes, with SHA-256
`294abbd203e48280fe30f639af4392d6708560e0bee69cf835b27797e04d32de`;
the preceding executable has the same aligned file size and SHA-256
`958e8a095261925d52beb4828d6515a8c7533d9bfb43221755e7a64a96bdb89b`.

The [machine-readable record](2026-09-05-spec16-block-local-float-folding.json)
contains the exact three campaigns, executable hashes, numerical checks and
the rejected `FABS` experiment. Each retained campaign excludes one warmup
and alternates seven processes.

| Family | Candidate | Previous | Clang slots8 | Silex/Clang | Result |
| --- | ---: | ---: | ---: | ---: | --- |
| Contact | 100.351 ms | 101.216 ms | 36.986 ms | **2.7132** | ranges overlap |
| Integration | 144.315 ms | 150.035 ms | 49.317 ms | **2.9263** | **3.812% reduction** |
| Preparation | 512.010 ms | 515.324 ms | 214.390 ms | **2.3882** | ranges overlap |

The integration ranges are disjoint: 142.807–146.296 ms after versus
148.087–155.797 ms before. Contact ranges are 99.802–101.177 ms after and
100.920–102.174 ms before. Preparation ranges are 487.552–517.143 ms after
and 510.327–520.312 ms before. No timing change is claimed for the latter two.
All MAD values are below 1%.

Contact passes 1,280 comparisons with maximum Silex error 6.4e-7.
Integration and preparation pass their short and complete 32,768-record Box2D
checks. Integration retains the previously published independent-trajectory
FMA divergence while every replayed transition from identical inputs passes;
this optimization does not change its numerical output.

Validation passes 1,186 compiler tests, 162 language tests, `zig build check`,
the optimizer qualification gate with 10 fixed regressions, 8 generated native
scenarios, 128 deterministic programs and 32 LLVM differential programs,
`compare 11`, and all 176 Physics tests. The new regressions cover finite
float folding in a branching function and preserve explicit division by zero,
infinity and NaN arithmetic.

Before this retained change, the `copysign`-to-`FABS` prototype was fully
qualified and rejected. Its integration median was 154.396 ms versus
153.632 ms before, with overlapping ranges; its ratio was 3.0137. The exact
patch and stash remain preserved outside the repositories.

The three same-layout ratios remain above one, so Part 16 stays active and no
`complete-part` candidate is registered. Parts 17 to 21 remain untouched.
