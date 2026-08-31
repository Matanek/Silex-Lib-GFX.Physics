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

The consumer proof is
[`DebugDraw.sx`](../../Tests/Consumer/Tests/DebugDraw.sx). The visual example
uses metres, `(0, -9.81) m/s²` gravity, and a fixed 60 Hz step. Bodies fall
continuously onto a ramp, chain, and floor while the joint gallery is driven.
Every layer rewrites one retained Canvas and an `FPSPanel` reports the measured
render cadence. Run it from the workspace root:

```text
silex run Silex-Examples/Sources/PhysicsDebugDraw2D/Main.sx --release
```
