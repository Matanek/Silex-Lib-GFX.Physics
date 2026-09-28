# Simulate rigid bodies in 3D

`World3D` simulates fixed, kinematic, and dynamic bodies without a window,
scene, renderer, or ECS. It accepts `Shape3D` spheres, boxes, and capsules and provides
a contact response between these shapes. Boxes resting on nearly parallel
faces use multiple points; fast motion can still pass through an obstacle.

An immutable `Compound3D` may also be the shape of a **fixed** body. The
world tests its primitive children and exposes `Contact3D.first_child_id()`
and `second_child_id()` for the selected child; `-1` denotes a primitive.
The contact currently selects the child with the smallest signed separation,
with one manifold per body pair. Dynamic and kinematic compounds are
rejected. Dynamic compound mass, mutation, and terrain support remain to be
delivered.

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
sphere, box, or capsule. `MassProperties3D` can specify positive mass, a local center,
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

## Connect two bodies by distance

`create_distance_constraint(first, second, settings)` connects two local
anchors in the same world. `DistanceConstraint3DSettings(length)` initially
sets an exact length; its `minimum_length` and `maximum_length` fields also
allow a range. Lengths must be finite, non-negative, and ordered. At least one
body must be dynamic; a fixed body can anchor the constraint to the world.
Active constraints share velocity iterations with contacts and also correct
position error.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var anchor = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed
        ..transform = Physics.Transform3D(position:Math.Vec3(0.0, 3.0, 0.0)))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..transform = Physics.Transform3D(position:Math.Vec3(0.0, 1.0, 0.0)))
    var tether = world.create_distance_constraint(
        anchor, weight, Physics.DistanceConstraint3DSettings(2.0))
    world.step(1.0 / 60.0)
    assert(Math.abs(tether.current_length() - 2.0) < 0.01)
}
```

`first_local_anchor` and `second_local_anchor` position the attachment points
in each body's local frame. `current_length()` measures their world-space
separation. `reaction_force()` reports the force applied to the second body
during the last positive step, in mass × distance / second²; it is zero for an
inactive constraint or a step with no impulse. `set_limits(minimum, maximum)`
and `set_enabled(enabled)` wake both bodies and clear the previous reaction.
`destroy_distance_constraint` invalidates the handle; destroying a linked
body invalidates its constraints as well. `distance_constraint_count()` counts
live constraints. A zero step preserves poses and observations.

## Connect two bodies at a point

`create_point_constraint(first, second, settings)` makes two local anchors
coincide in all three directions while leaving body orientations free.
`PointConstraint3DSettings()` puts both anchors at their local origins by
default; set `first_local_anchor` and `second_local_anchor` for the intended
pivot. Anchors must be finite and at least one body must be dynamic. Collisions
between linked bodies remain active: anchors that force the shapes to overlap
can put the joint and contact response in opposition.

`anchor_error()` returns the vector from the first world anchor to the second.
`reaction_force()` reports the force on the second body during the last
positive step. `set_anchors(first, second)` and `set_enabled(enabled)` wake
the linked bodies and clear the stored reaction. A zero step preserves these
observations. `destroy_point_constraint()` and destruction of a linked body
invalidate the handle; `point_constraint_count()` counts live joints. Point
joints share steps, contacts, and sleep islands with rigid distance joints.

Both families are rigid. Springs, motors, and other 3D joint families remain
to be delivered. Very fast motion may still cross an obstacle because the
world has no CCD.

## Query bodies in the world

`ray_cast(ray, ignore_body)` returns the nearest `Ray3D` hit or `null`.
`write_ray_hits(ray, output, ignore_body)` fills a reusable array with one
hit per body, ordered by increasing fraction. For a compound, that hit comes
from its nearest child; `child_id()` gives its ID and is `-1` for a primitive.
Each `WorldRayHit3D` also exposes `body()`, `point()`, `normal()`, and a
`fraction()` between 0 and 1.

`write_overlaps(query, output, ignore_body)` selects bodies overlapping a
`ShapePlacement3D`. Each `WorldOverlap3D` provides `body()`,
`query_child_id()`, and `body_child_id()`; results follow world slot order.
Disabled bodies are excluded from both queries. The optional `ignore_body`
excludes a live body from the same world, such as the ray's emitter. A foreign
or destroyed body is rejected.

Copied points, normals, fractions, and IDs remain readable after later steps
or destruction. The `body()` handle keeps its identity, but `is_valid()`
becomes false when that body or its world is destroyed. Category filtering
and sensors will be added separately; these queries do not change contacts.

## Sleeping and waking

Dynamic bodies allow sleep by default. Their `sleep_threshold` is 0.05 for
linear and angular speed, and must be finite and non-negative. Use
`allow_sleep`, `set_sleep_enabled`, `set_sleep_threshold`, `is_awake`, and
`wake_up` to control this behavior. Fixed and kinematic bodies are not
reported as awake. A free body can sleep without gravity; under gravity, a
dynamic island needs contact or an active constraint with a fixed or
kinematic body before it can
sleep. All bodies in an island must remain below their thresholds together
for 0.5 seconds of fixed steps. Their velocities then become zero and their
poses stop drifting.

A velocity, force, torque, impulse, mass, pose, or material command wakes the
affected body; changing a support can wake other bodies in the world. A new
collision and support removal also wake affected bodies. Waking one member
propagates through contacts, distance constraints, or point constraints on the next step. `step(0)` changes neither sleep
nor the latest contacts. Contacts between sleeping bodies remain observable,
with zero impulse applied during the inactive step.

## Gravity and integration

Default gravity is `(0, -9.81, 0)`. `gravity_scale` is set per body at
creation; linear and angular damping default to zero. Forces and torques
accumulate until the next positive step, then clear. A zero step moves no
body and preserves those accumulations. Integration uses semi implicit
velocity and keeps a normalized quaternion; results depend on step size.

## Read contacts

After a positive step, `contact_count()` counts detected pairs and
`write_contacts(output)` copies their observations to a caller-owned array.
Each `Contact3D` exposes the two handles, the centroid of its manifold points
as a representative point, response normal, separation measured before
correction, and the sum of applied normal impulses. `point_count()` and
`write_points(output)` expose the manifold;
each `ContactPoint3D` contains a world position and its normal and tangential
impulses. Negative separation means penetration; the step then moves dynamic
bodies back toward tangency and responds to incoming velocity at the contact
points. If a sphere starts inside
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
dynamic body. A positive separation below `10⁻⁶` may retain a resting pair
despite rounding; standalone queries keep the measured separation. For two
boxes, it clips the incident face to the reference face bounds, discards
points above that face, and keeps up to four distributed supports. This bounded
work runs for each contacting box pair at every step. Nearby point impulses
carry into the next step while the same handles and contact orientation
remain. Nearly parallel capsules can
retain two lateral points; other configurations still use one point. A small
stack and initially tilted boxes on a flat floor stabilize with the tested
fixed step. Edge-to-edge contacts and sliding supports may still drift; there
is no CCD or static friction guarantee.
`step(0)` preserves the last observations; destroying a body removes current
contacts that refer to it. A retained snapshot keeps its measurements, but
its handles become invalid with their bodies or world.

## Contact begin and end

After each positive step, `write_contact_begin_events(output)` and
`write_contact_end_events(output)` copy `Contact3D` snapshots into caller
arrays. A begin occurs once for a new body and subshape pair; persistence
produces neither a begin nor an end. An end occurs on the first positive step
where the pair is absent. Moving from one compound child to another ends the
old child ID and begins the new one.

Destroying a body removes its current contact immediately and queues an end
for the next positive step. Disabling or moving a body apart is observed at
that step. `step(0)` retains the previous step's events and any pending ends.
Copied snapshots retain their point, normal, separation, and child IDs across
later steps. Their handles still support `is_valid()` and `same_body()`;
reading the state of a destroyed body remains invalid. Reusing a slot cannot
confuse the old body with the new one. A sleeping body may retain its contact
and does not emit an end solely because it sleeps.

## Ownership and lifetime

Each world owns its storage and bodies. `RigidBody3D` is a typed handle with
a generation: destroying a body invalidates every copy, even if its slot is
reused. Ending a world also invalidates retained handles; handles do not keep
the world alive. Use `is_valid()` to check them; any other read on a stale
handle fails explicitly. A world refuses to destroy another world's body.
`write_bodies` fills a caller-owned array with live bodies without promising
creation order.

The world does not yet provide integrated spatial queries or CCD.
[Standalone geometry queries](Geometry3D.md) remain
available for individual shapes.
