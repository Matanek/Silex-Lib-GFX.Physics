# Constraint preparation compiler witness

Compiler `4183a600a17a2cdbbce25cf33b5c5d37a2684537`, native Release,
macOS 26.6.2 ARM64, Apple M3 Pro. The [protocol](../Oracle2D/StageKernels.md)
maps the one-point preparation to Physics and the pinned Box2D implementation.
No production Physics source changes.

The [raw campaign](2026-09-03-spec16-preparation.json) records one excluded
warmup and seven serial processes per variant in rotating order. No task-owned
build, test or other benchmark ran concurrently. Every process prepares 8,192
contacts for 2,048 passes, cycling through 16 prebuilt input frames. All 26
output fields contribute to a per-pass weighted reduction that is included in
both languages' timing. This is preparation plus observation, not the isolated
cost of reciprocal arithmetic or a production-engine attribution.

| Variant | Median | Range | MAD |
| --- | ---: | ---: | ---: |
| Silex, slots8 | 5,390.581 ms | 5,380.968–5,415.119 ms | 0.155% |
| Clang, slots8 | 214.134 ms | 213.883–214.793 ms | 0.057% |
| Clang, packed | 157.231 ms | 157.117–157.603 ms | 0.073% |

Timing is admissible. Silex/Clang at identical layout is **25.1739**;
compiler parity fails. Clang slots/packed is 1.3619, with disjoint ranges:
the packed layout is faster in this streaming case. It is not substituted
for the matching-layout compiler comparison.

Debug and Release pass the first eight passes and the complete 851,968 scalar
comparisons against `b2PrepareOverflowContacts`. The adapter builds genuine
Box2D body/contact records and maps every tested output from that function.
All timed signatures match the fully checked outputs, including earlier passes.
Sixteen contact/stage comparator tests pass. The extended shared runner also
revalidates integration against the exact existing binaries; no new integration
timing is claimed. No native X64 execution or performance claim follows.

All three required algorithm families now have witnesses. The latest contact,
integration and preparation ratios are respectively 9.0783, 45.3167 and 25.1739;
all miss parity. These are separate campaigns and must not be pooled into an
engine-wide ratio. General compiler work and the required native target gates
remain open.
