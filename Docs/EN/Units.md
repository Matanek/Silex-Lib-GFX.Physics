# Use pixels or centimeters

The Physics world uses meters, seconds, and kilograms. If your application
stores pixels or centimeters, convert its lengths before creating shapes,
bodies, and queries. Convert results back for rendering. The application scale
does not change the world's physical constants.

At 100 application units per meter, a position of 300 units becomes 3 m and
a radius of 25 units becomes 0.25 m. This complete example checks those
conversions through the public API:

```silex
use GFX.Physics
use STD.Math

func main() {
    let units_per_meter = 100.0
    var world = Physics.World2D(gravity:Math.Vec2(0.0, -981.0).divide(units_per_meter))
    var body = world.create_rigid_body(Physics.RigidBody2DSettings()
        ..shape = Physics.Shape2D.circle(Physics.Circle2D(25.0 / units_per_meter))
        ..position = Math.Vec2(0.0, 300.0).divide(units_per_meter)
        ..velocity = Math.Vec2(100.0, 0.0).divide(units_per_meter)
        ..allow_sleep = false)
    world.step(1.0 / 60.0)
    let application_position = body.position().multiply(units_per_meter)
    assert(application_position.x > 0.0)
    assert(application_position.y < 300.0)
    print("application-units-ok")
}
```

Here gravity is −981 units/s², or −9.81 m/s². Mass remains in kg and the time
step in seconds. For Scene2D, the `scene_units_per_meter` setting in
[Application integration](ApplicationIntegration.md) handles scene position
conversion; shape dimensions still follow the Physics contract.

## Convert dimensional quantities

For `u` application units per meter, input conversions are:

| Quantity expressed in the application | Value to pass to Physics |
| --- | --- |
| Position, length, radius, query translation | value / `u` |
| Velocity, acceleration, force, linear impulse | value / `u` |
| Torque, inertia, angular impulse | value / (`u` × `u`) |
| Surface density in kg/unit² | value × `u` × `u` |
| Mass in kg, duration in seconds, angle in radians, angular velocity | unchanged |
| Frequency in Hz, damping ratio, friction, restitution | unchanged |

These rules assume that application mass and time already use kilograms and
seconds. A force already expressed in newtons needs no conversion: the factor
only applies to quantities expressed using the application's length unit.
Output conversions reverse this table. A ray or shape-cast fraction is
dimensionless and remains unchanged.

## Preserve physical thresholds

Sleep, hit, and restitution thresholds are velocities in m/s. Thus 1 m/s
corresponds to 100 units/s at this scale. Keep the Physics values when only
rendering changes units; convert a custom threshold supplied by the application.
[World settings](WorldSettings.md) lists the defaults.

The [executable witness](../../Benchmarks/UnitsOracle2D.sx) and Box2D oracle
compare representations at 1 and 100 units/meter: rest, rays, shape casts,
CCD placement, restitution and hits below and above 1 m/s, sleep below and above
0.05 m/s, and the 400 m/s speed cap. Checks are maintained in
[CheckUnits.py](../../Benchmarks/Oracle2D/CheckUnits.py). This evidence covers
those scenes and tolerances; it does not guarantee every scale or simulation.
The previously documented velocity difference immediately after CCD placement
is not removed by changing units.

Changing display units does not make a physically tiny object larger for the
solver or increase floating-point precision. Keep physical coordinates near
their useful region; do not multiply world coordinates directly by 100 while
leaving its tolerances in meters.
