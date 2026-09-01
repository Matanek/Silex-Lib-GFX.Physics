# Physics debug draw

`World2D.write_debug_snapshot` transforms the last completed step into an
autonomous list of lines, circles, and labels. The snapshot retains no internal
handle, callback, or world lock, so it may be rendered later or at a different
rate from the simulation.

```silex
use GFX.Physics

var snapshot = Physics.World2DDebugSnapshot()
let settings = Physics.World2DDebugSettings()
    ..bounds = true
    ..contacts = true
    ..contact_normals = true
    ..labels = true

world.step(1.0 / 60.0)
world.write_debug_snapshot(settings, snapshot)

var drawing = Physics.World2DDebug.canvas(snapshot)
var scene_canvas = Physics.World2DDebug.scene_canvas(snapshot)
```

Layers cover shapes, joints, AABBs, centers of mass, labels, contacts, normals,
impulses, islands, and constraint-graph colors. Every color is customizable
through `World2DDebugTheme`. An optional
`World2DDebugRegion(lower, upper)` removes primitives outside the visible
region before they are written.

Defaults enable only shapes and joints. Setting `enabled` to `false` clears the
snapshot without traversing the world. Reusing one `World2DDebugSnapshot`
retains its storage capacities; after a sufficiently large first write,
`storage_growth_count()` stays stable while the primitive count does not grow.

The renderer can write to a supplied `GFX.Canvas.Canvas` with `draw`, create a
new Canvas with `canvas`, or create a `GFX.Scene2D.Canvas` component with
`scene_canvas`. It remains a diagnostic facility, not the final game
representation.

For an open chain, the `shapes` layer draws only the colliding segments. The
two ghost segments around its endpoints remain hidden so the diagnostic does
not suggest a solid surface that is not present.

The consumer proof is
[`DebugDraw.sx`](../../Tests/Consumer/Tests/DebugDraw.sx). Two visual examples
separate the diagnostic intentions. The first uses metres, `(0, -9.81) m/s²`
gravity, and a fixed 60 Hz step; bodies fall continuously onto a ramp, a chain,
and a floor. Its fixed labels live in an immutable vector Canvas, while the
geometric Canvas is rewritten only after a physics step. The second places all
eight joint families under the same SI gravity as suspended mechanisms: spring
mass, filtered pendulums, servo, soft target, slider, hinged pendulum, welded
pair, and wheel suspension. The mouse joint's world target is part of the
diagnostic drawing. Each example displays its cadence with `FPSPanel`:

```text
silex run Silex-Examples/Sources/PhysicsDebugDraw2D/Main.sx --release
silex run Silex-Examples/Sources/PhysicsJointDebugDraw2D/Main.sx --release
```
