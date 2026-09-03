# Retained solver and comparison infrastructure qualification

The retained production solver passes its correction gates. This checkpoint
establishes a reproducible starting candidate; it does not establish complete
Box2D capability coverage, engine performance parity, or the final RSS budget.
The existing performance failures remain failures.

## Qualified inputs

The solver changes separate warm-start data from completed contact snapshots,
retain speculative circle pairs, classify compact-circle eligibility once per
body and step, and share body views through the constraint solve. Disabling a
contact policy restores the cached allowance. Soft Step performs one biased
solve and one unbiased relaxation per substep, with friction in both passes.

The three source files are byte-for-byte identical to the retained checkpoint;
no additional solver or compiler optimization was introduced during this
qualification. Only the descriptions of the old solve schedule were corrected.

| Input | Commit or SHA-256 |
| --- | --- |
| Silex compiler | `bd0e76b6ab494f72e96d409cdd071169237160f3` |
| Physics instrumentation before this commit | `7e7e979929c1c146da211f4a7a24cd938cf0fa1a` |
| `Module/World2D.sx` | `fa36243cf873f1eac7450d2497c75a4eefe1758a88c1aee58e4ac2861a0d7c64` |
| `Tests/CompactContacts2D.sx` | `ec0cec95103e0652aebe4dc9f069a0aa2a922c9ddf5fe0e85781dc39121121f9` |
| `Tests/SoftStepSchedule2D.sx` | `4ba1cb5b8afc159800d6dffa00e616f638382bf32b89e6ae3e1335ac0c660bed` |
| GFX.Scene2D | `95bf54c15d214cd641425946a95f1be78d81c9f5` |
| Silex-Examples | `35406fc8a3ecf45c8b21719ac16f520cc57bf205` |
| STD | `5a018305fb470dfe00e94466150b3c04f207e252` |
| Box2D 3.1.1 | `8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3` |

Qualification ran on Apple M3 Pro ARM64, macOS 26.6.2, with Zig 0.16.0.
Physics and Scene2D resolve through workspace-local links to the candidate
group. The anonymous `Tests/Consumer` package resolves those same candidates.
The other resolved packages were clean: GFX `7e8814a`, GFX.Application
`e7cfa74`, GFX.ECS `0fb019c`, GFX.Canvas `4a382c6`, GFX.Assets `75170e3`,
GFX.Font `7208e81`, GFX.GPU `9cb3dd0`, GFX.Rendering `913d77b`, JSON `046f641`.

## Green correction gates

- Compiler: `zig build check -Doptimize=Debug`, `zig build test`,
  `zig build optimizer-gate`, and `zig build optimizer-oracle -- compare 11`.
- Physics: 176 tests in 28 files, without the reusable Silex cache. This
  includes public consumers, contact snapshots and events, material and shape
  mutation, the 1/2/4/8-substep schedule, and existing parallel-solver tests.
- All ten `Tests/Consumer/check-*.sh` diagnostic scripts pass, including
  reentrant policies, invalid settings and stale handles.
- All ten existing differential witnesses pass their unchanged checkers:
  geometry, body control, dynamic shapes, continuous collision, contact
  policies, contact snapshots, world queries, character mover, explosions,
  and joints. The CCD witness retains its three documented response
  divergences; passing it does not prove global behavioral parity.
- `CheckedMemoryLanes.sx` and `AggregateControlFlow.sx` pass explicit native
  Debug, native Release and interpretation.
- The contact kernel passes in explicit Debug and Release against the actual
  pinned Box2D function: 128 states and 1,280 scalar comparisons per variant.
  Maximum absolute error is `6.4e-7` for Silex and `9.5e-7` for the two C
  variants, below the unchanged `2e-6` tolerance.
- The 18 comparator tests pass, including incomplete/duplicate states,
  non-finite values, configuration mismatches, changed signatures, insufficient
  series, and missing or inconclusive parity.
- The public corpus passes the `release-parity` correction scene in explicit
  Debug and Release. A fresh Release `circle-5000 --box2d-parity` run preserves
  signature `-83418950`, overlap `16.319561 mm`, all 5,000 bodies awake,
  18,117 persistent pairs/constraints and 17,947 compact constraints.
- The compiler witnesses and the public corpus emit ELF Linux X64 and PE
  Windows X64 artifacts. These artifacts were not executed on those systems.
- FallingBodies, PhysicsDebugDraw2D and ShapeResponse compile in Release
  against the cumulative candidate. This is no visual acceptance claim.

Run source-compiling commands from the candidate group root with
`Silex/Toolchain/zig-out/bin/silex` and explicit input paths. Run Zig commands
from that group's `Silex/Toolchain`. Set `ZIG_GLOBAL_CACHE_DIR` to a writable
Zig cache when the host's global cache is restricted; the initial permission
failure was environmental, and all four compiler commands passed on retry.
The [oracle protocol](../Oracle2D/README.md) gives the differential commands.

## Gates deliberately still red

The ten archived before/after engine campaigns were rechecked separately
with `CompareCorpus.py`. Each exits 1 solely for exceeding performance parity.
The last matched dense ratio remains **9.183950×** in
[`2026-09-03-spec15-affinity-after.jsonl`](2026-09-03-spec15-affinity-after.jsonl).

Both archived RSS series still fail `CheckCorpus.py --enforce` solely on their
storage budget. The last series has an incremental RSS of **15,532,032 B**
against **14,395,904 B**, a **1,136,128 B** overrun.

Recomputing the statistics of
[`2026-09-03-spec15-contact-kernel.json`](2026-09-03-spec15-contact-kernel.json)
reproduces its stored summaries and `compiler_parity: missed`, with the
**14.2588×** same-layout ratio. The kernel runner and engine comparator retain
their strict parity conditions. No threshold, tolerance or baseline was
weakened to qualify this starting point.

No new performance campaign was recorded during this stabilization. Fresh
consumer runs are correction evidence only. Native compiler cost, whole-engine
pipeline alignment, complete capability coverage, worker assembly, engine
timing/RSS and final platform/visual acceptance remain separate follow-up
gates. Existing unit tests do not replace those final proofs.

Local qualification logs and fresh binaries are retained under
`/private/tmp/spec15-resume-01a06651/`. Fresh Release executable SHA-256:
corpus `f0e3551557b4e26f679fb9cd1d32cdda6cf72130adc387f3127b45e2a466bcbb`,
contact kernel `89156849dba532d4c99fced27aacac2b19d03f312599272a7b0f7299642240ed`.
