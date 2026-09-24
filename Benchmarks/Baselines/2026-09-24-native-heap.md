# Native macOS ARM64 heap and rotating CCD

`RotatingContainerCost2D.sx` isolates the rotating-kinematic collision path
seen in the `RotatingPhysicsContainer` example. It runs 24 fixed steps with
16 mixed dynamic bodies and four moving walls, without graphics, ECS or
wall-clock-dependent spawning. Continuous collision detection stays enabled.
This is a short diagnostic, not a statistical backend qualification.

The Native compiler at `e1b920007babeb04c61ec8808cb4eedcb6a0a811` allocates
even small objects through `mmap`/`munmap`. Compiler
`0c22065c12c0c5dcf3f600abaaff1d95e91f831b` uses libSystem `calloc`/`free`
on Darwin ARM64, including the temporary convex proxies and simplex objects
created by collision queries. Physics code is unchanged between the runs
(solver revision `e8f025ce8e48430c27abbd72638e03e0b43b9544`).

Release measurements on macOS ARM64, before/after then after/before:

| Pair | Before, ms/step | After, ms/step |
| --- | ---: | ---: |
| 1 | 16.48275 | 2.50975 |
| 2, reversed | 17.06154 | 1.7019583 |

All four sets of `STATE` lines have SHA-256
`d80f46011758b31ff06f82bb21d5e118b63af0c57bc666833670d5888b1093e0`.
The candidate also passes the eight `ContinuousCollision.sx` consumer tests.
Timing variation remains visible; the result establishes a large allocator
cost, not an exact speedup or a whole-application FPS guarantee.

Build each pinned compiler first, then compile this same source in Release
with `--backend native --nocache`, from the workspace root (or the Spec's
isolated Worktree root). Run the resulting executables sequentially without
concurrent builds. Hash only lines beginning with `STATE `; the timing header
is deliberately excluded. Do not replace this witness with different body
counts, fewer substeps or disabled continuous collisions.
