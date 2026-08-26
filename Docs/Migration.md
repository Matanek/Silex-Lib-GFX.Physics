# Migrating from GFX.Physics 0.4 to 0.5

GFX.Physics 0.5 switches the package to the native Silex reconstruction based
on the Box2D 3 algorithmic model. `Physics.World2D` remains the only public
world: there is no backend selector, compatibility engine, or second package
to configure. Box2D remains a pinned benchmark oracle and is not linked into
applications.

## Existing source remains valid

The 0.4 intention surface is retained:

- `World2D`, its `gravity` constructor argument, `step`, profiling, explicit
  worker count, body counts, candidate counts, and transform writers;
- `RigidBody2DSettings`, including its default box, body type, transform,
  motion, mass, material, damping, gravity scale, and sleep settings;
- `RigidBody2D` transform, velocity, gravity, awake-state accessors and
  mutators;
- the `GFX.Components.RigidBody2D` and `GFX.Resources.World2D` catalog aliases.

[`../Tests/Consumer/Tests/Compatibility.sx`](../Tests/Consumer/Tests/Compatibility.sx)
compiles and executes that complete 0.4 path from an isolated consumer. An
ordinary application does not need a source migration merely to select the new
core.

## Intentional behavior changes

The switch changes internal simulation behavior without exposing its
architecture:

- all worker counts now use the same deterministic pair discovery, contact
  cache, island graph, and four-substep Soft Step solver;
- exact floating-point trajectories from the former solver are not a
  compatibility guarantee; applications should assert physical envelopes and
  gameplay outcomes rather than old bit patterns;
- body handles now keep stable generational identity, and
  `destroy_rigid_body` invalidates every retained copy explicitly;
- the world rejects body, joint, and world mutation while `step` is active;
- the retained API adds convex geometry queries, persistent contacts, joints,
  bullets, sensors, and opt-in completed-step event streams.

Applications only opt into the new costs they request. Ordinary bodies do not
enter bullet CCD, disabled event streams do not construct event payloads, and
parallel execution never selects a different solver.

## Release boundary

The 0.5 version reflects cumulative public additions and intentional behavior
changes since 0.4. The package is pure Silex and owns no platform boundary.
Local macOS execution and public-consumer tests validate the package contract;
the final release remains separately gated by the workspace portability
matrix, graphical sentinels, benchmark corpus, and visual ShapeGallery review.
