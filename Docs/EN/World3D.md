# Simulate rigid bodies in 3D

`World3D` simulates fixed, kinematic, and dynamic bodies without a window,
scene, renderer, or ECS. It accepts `Shape3D` spheres and boxes and provides
a first contact response between these shapes. Multiple contacts are not yet
stabilized; fast motion can pass through an obstacle.

The following program applies an impulse to a box, advances the world, and
reads its position. Impulse uses mass × distance / second units.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings()
        ..gravity = Math.Vec3())
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0))))
    body.apply_impulse(Math.Vec3(8.0, 0.0, 0.0))
    world.step(0.25)
    assert(body.position().nearly_equal(Math.Vec3(0.25, 0.0, 0.0), 0.00001))
    world.destroy_rigid_body(body)
    assert(!body.is_valid())
}
```

## Poses, mass, and commands

Coordinates follow `STD.Math`: right handed, with Y up.
`Transform3D.position` locates the shape origin; `rotation` is a unit
quaternion. Linear and angular velocities use world coordinates.
`world_center_of_mass()` returns the center of mass, which can differ from
the shape origin. Angles and angular velocities use radians. `step(delta)`
takes seconds and rejects negative or non-finite values.

Bodies are dynamic by default, with a radius 0.5 sphere and density 1. Mass
and the three principal moments of inertia are derived for a homogeneous
sphere or box. `MassProperties3D` can specify positive mass, a local center,
and three positive local moments; the principal axes then align with the
shape's local axes. Inertia is rotated into world coordinates for torque and
impulses. A force or impulse with a world application point also creates a
moment around the center of mass. `apply_torque` and
`apply_angular_impulse` act directly on rotation.

A fixed body keeps its pose and rejects forces and impulses. A kinematic body
moves with configured velocities; `move_kinematic(target, duration)` computes
velocities to reach a pose at a specified time, then clears them. It reaches
the target exactly when a step covers the end of the duration.
`set_transform`, `set_linear_velocity`, `set_angular_velocity`,
`set_enabled`, and `set_mass_properties` support direct changes. Only a
dynamic body accepts a mass override.

Default gravity is `(0, -9.81, 0)`. `gravity_scale` is set per body at
creation; linear and angular damping default to zero. Forces and torques
accumulate until the next positive step, then clear. A zero step moves no
body and preserves those accumulations. Integration uses semi implicit
velocity and keeps a normalized quaternion; results depend on step size.

## Read a first contact

After a positive step, `contact_count()` counts detected pairs and
`write_contacts(output)` copies their observations to a caller-owned array.
Each `Contact3D` exposes the two handles, point, response normal, separation
measured before correction, and applied normal impulse. Negative separation
means penetration; the step then moves dynamic bodies back toward tangency
and responds to incoming velocity at the contact point. If a sphere starts inside
a box, the response normal can be opposite to the `Geometry3D.distance`
query normal so the sphere exits through the nearest face.

Each body selects `friction` (0.6 by default) and `restitution` (0 by
default) in `RigidBody3DSettings` or through `set_material`. Friction must
be finite and non-negative; restitution must be finite in `[0, 1]`. A pair
uses the geometric mean of friction and the greater restitution. A normal
impact faster than 1 receives restitution; slower impacts do not bounce.
Tangential impulse is bounded by combined friction times normal impulse.
`Contact3D.friction()`, `restitution()`, and `tangent_impulse()` expose these
step results.

Detection currently examines every pair of enabled bodies with at least one
dynamic body. It handles one point per pair and has no manifold cache,
persistent static friction, or CCD. Stacks and oblique contacts can still drift.
`step(0)` preserves the last observations; destroying a body removes current
contacts that refer to it. A retained snapshot keeps its measurements, but
its handles become invalid with their bodies or world.

## Ownership and lifetime

Each world owns its storage and bodies. `RigidBody3D` is a typed handle with
a generation: destroying a body invalidates every copy, even if its slot is
reused. Ending a world also invalidates retained handles; handles do not keep
the world alive. Use `is_valid()` to check them; any other read on a stale
handle fails explicitly. A world refuses to destroy another world's body.
`write_bodies` fills a caller-owned array with live bodies without promising
creation order.

The world does not yet provide materials, sleeping, constraints, spatial
queries, or CCD. [Standalone geometry queries](Geometry3D.md) remain
available for individual shapes.
