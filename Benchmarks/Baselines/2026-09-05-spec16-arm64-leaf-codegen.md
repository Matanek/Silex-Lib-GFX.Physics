# Part 16 ARM64 leaf code generation

This checkpoint records five cumulative Silex compiler corrections after
`d91342aaf02e4c15fab8296135d63f1fe0aa53cd`, ending at
`c72eac797a13e2a9fab1a01e6af055f15bded370`:

- correct floating-point SSA promotion across diamonds and loop back-edges;
- remove overflow checks from the first increment proven by a zero-origin
  bounded loop header;
- remove status branches after proven-infallible direct calls and let the
  successful ARM64 return fall through to the epilogue;
- precolor call-free scalar parameters away from incoming argument registers,
  then prefer volatile registers for leaf temporaries;
- omit an ARM64 frame only when every materialized participant is resident,
  there are at most eight parameters, no call crosses the function, and no
  callee-saved register or cycle context is required.

The final correction is deliberately all-or-nothing. One spill retains the
complete deterministic frame and all original slot offsets. Individually
unused leaves of borrowed aggregate loads do not count because their encoder
path already emits no load or store. A cycle context is still reserved for
every function containing `class_drop`.

For the integration witness, both hot helpers become genuinely frameless.
`integrate_velocity` falls from 108 to 103 ARM64 instructions and
`integrate_position` from 47 to 42; each loses its only two stack/frame
references. Contact and preparation retain their real stack traffic and the
same instruction counts as the preceding commit.

All three final binaries pass their short and complete Box2D checks. Contact
checks 1,280 scalar values with maximum error 6.4e-7. Integration and
preparation each check 32,768 records; integration replays every transition
from identical candidate inputs through Box2D, while preparation compares
every prepared field from identical inputs.

The retained repeat campaign alternates seven fresh processes after a warmup:

| Family | Candidate | Previous commit | Clang slots8 | Current ratio | Candidate / previous |
| --- | ---: | ---: | ---: | ---: | ---: |
| Contact | 98.853 ms | 98.625 ms | 41.590 ms | **2.3768** | 1.0023 |
| Integration | 95.863 ms | 101.172 ms | 50.846 ms | **1.8854** | **0.9475** |
| Preparation | 518.186 ms | 511.127 ms | 232.153 ms | **2.2321** | 1.0138 |

Integration is demonstrated: candidate range 95.428–97.305 ms is below the
preceding range 100.300–102.422 ms, a 5.247% median reduction. Contact and
preparation ranges overlap and their point changes are treated as noise. All
MAD values are below 1.1% and all medians exceed 20 ms.

The exact candidate passes 1,192/1,192 Silex tests, including 162 language
tests. The ReleaseFast optimizer qualification passes 12 fixed regressions
and 8 generated native scenarios. The machine-readable companion records
binary and raw-campaign hashes. Raw executables, disassemblies and campaigns
remain under `/private/tmp/spec16-01a070df`; the earlier rejected low-leverage
encoder patch remains archived there as well.

These are current admissible point estimates, not a new final cumulative
qualification of Part 16. Every ratio remains above one, so Part 16 stays
incomplete and no `complete-part` action is valid. Parts 17 through 21 were not
modified.
