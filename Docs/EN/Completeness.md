# Box2D 3.1.1 completeness contract

GFX.Physics targets useful behavioral parity with the stable rigid-body 2D
capabilities of Box2D 3.1.1 at commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`. It does not copy Box2D's C names,
handles, callbacks or storage model into the Silex API.

The executable source of truth is
[`../Benchmarks/Oracle2D/CompletenessMatrix.json`](../../Benchmarks/Oracle2D/CompletenessMatrix.json).
Its validator parses all `B2_API` declarations from `base.h`,
`math_functions.h`, `types.h`, `collision.h` and `box2d.h` in the pinned
checkout. The current inventory contains 422 symbols, each owned by exactly one
of 59 behavioral capability rows. A changed revision, header count, missing
symbol, duplicate classification, missing proof, absent future Spec or
unjustified exclusion fails validation.

## Status language

| Status | Meaning | Required matrix support |
| --- | --- | --- |
| `covered` | The useful behavior is available now. | An executable test, example or differential witness. |
| `partial` | A useful subset is proven, but the complete gameplay behavior is not yet available. | Current evidence and the named future Spec. |
| `planned` | The gameplay capability is absent and retained by this sequence. | The named future Spec. |
| `divergent` | Silex deliberately expresses the same intention differently. | A consumer proof and a testable rationale. |
| `excluded` | The symbol is integration plumbing or a non-gameplay implementation control. | An explicit rationale. |

The current contract contains 25 covered, 5 partial, 17 planned, 4 divergent
and 8 excluded capability rows. These counts describe groups of related
behavior, not percentages of engine completeness. The final sequence gate removes every
unexplained partial or promise; it does not promote a capability by counting C
wrappers.

## Intentional boundary

The public Silex model keeps shapes as `Shape2D` values and exposes their
living instances as stable `Collider2D` handles. World queries write typed,
deterministically ordered results instead of invoking traversal callbacks.
Contact policies execute on the world-owning thread and return immutable
decisions instead of receiving context pointers from solver workers. Physics
uses fixed meter-second-kilogram units rather than mutable process-global
scaling.

Allocator hooks, assertion hooks, generic clocks and hashes belong to the
compiler, STD or host runtime. Raw dynamic-tree proxies, rebuild controls,
solver test switches and memory dumps remain private. `userData` pointers are
excluded at world, body, collider and joint levels; typed handles, material
identifiers, debug labels and application maps cover those intentions without
untyped lifetime hazards.

Cloth, soft bodies, fluids and 3D are outside this rigid-body 2D contract.
Box2D remains a benchmark-only oracle and is never linked into a GFX.Physics
consumer or runtime package.

## Validation

From the workspace root, after configuring the pinned oracle checkout:

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCompleteness.py \
    --box2d-source /tmp/silex-box2d-v3.1.1
```

Pass `--report /tmp/gfx-physics-completeness.md` to expand every capability row
into its exact Box2D symbol list for review. The generated report is disposable;
the reviewed JSON matrix remains the durable contract.

Both corpus executables emit schema-2 `SILEX_PHYSICS_CORPUS` records with the
same version and configuration vocabulary: `engine_version`,
`oracle_version`, `oracle_revision`, `solver` and `substeps`, alongside build
mode, worker count, scenario and timestep. Historical schema-1 baselines remain
readable, while every newly produced schema-2 record is rejected if the pinned
oracle metadata or configuration fields are missing.
