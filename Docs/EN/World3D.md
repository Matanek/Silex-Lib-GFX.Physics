# Simulate rigid bodies in 3D

`World3D` simulates fixed, kinematic, and dynamic bodies without a window,
scene, renderer, or ECS. It accepts `Shape3D` spheres, boxes, and capsules and provides
a contact response between these shapes. Boxes resting on nearly parallel
faces use multiple points. Dynamic bodies can opt into linear continuous
collision for fast motion.

A `Triangle3D` may be the shape of a **fixed** body. It responds to dynamic
spheres on the front side defined by vertex winding, including exposed edges
and vertices; a sphere whose center is behind the triangle plane creates no
contact. The triangle and its pose can be replaced without recreating the body.
Dynamic or kinematic triangle bodies and triangle children in compounds are
rejected. Triangle/box, triangle/capsule, triangle/triangle contacts, mesh
seams, terrain, and CCD against triangles are not qualified. Physics triangles
are independent of render geometry.

An immutable `Compound3D` can be the shape of a fixed, kinematic, or dynamic body.
Each touching child pair owns a manifold, identified by
`Contact3D.first_child_id()` and `second_child_id()`; `-1` denotes a primitive.
Several contacts may therefore connect the same bodies. Events and cached
impulses distinguish both body identities and both child IDs, independently
of the compound's construction order. Sensors report the same pairs without
applying a response.

A kinematic compound uses `move_kinematic` or linear and angular velocities,
just like primitives. Children follow their parent pose; contact velocity
includes rotation around the body origin. It can wake and carry a dynamic
payload. Dynamic compounds of boxes, spheres, and capsules are also available:
the body's density applied to each child determines its mass, center of mass, and
inertia tensor. Child identities remain visible in contacts. Replacing an
existing body's shape is available; editing a `Compound3D` in place, other
shape families, and terrain remain to be delivered. Kinematic motion does not
add rotational CCD.

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
and inertia are derived for a homogeneous sphere, box, capsule, or compound
of these primitives. `MassProperties3D` accepts either three positive local
moments as a `Vec3` or a symmetric positive-definite tensor as a `Mat3`;
existing `Vec3` calls retain their local principal axes. The `inertia_tensor`
field contains the full tensor, while `local_inertia` contains its diagonal.
Offset or rotated compound children can produce cross terms that affect
impulses and rotation. Positive mass and a local center can also be supplied.
Inertia is rotated into world coordinates for torque and
impulses. A force or impulse with a world application point also creates a
moment around the center of mass. `apply_torque` and
`apply_angular_impulse` act directly on rotation.

A fixed body keeps its pose and rejects forces and impulses. A kinematic body
moves with configured velocities; `move_kinematic(target, duration)` computes
velocities to reach a pose at a specified time, then clears them. It reaches
the target exactly when a step covers the end of the duration.
`set_transform`, `set_linear_velocity`, `set_angular_velocity`,
`set_enabled`, `set_shape`, and `set_mass_properties` support direct changes. Only a
dynamic body accepts a mass override.

`body.set_shape(new_shape)` replaces a shape without changing the body's
identity, pose, material, or filter. To change a compound, build a new
`Compound3D` and pass it to this method; its children are not edited in place.
For a dynamic body, the density selected at creation derives the new mass,
center, and inertia tensor. This replaces any custom `mass_properties` override;
the override can be applied again with `set_mass_properties`. Linear velocity
is adjusted to preserve the velocity at the new center of mass, and affected
bodies wake. On the next step, contacts of the old shape end and contacts of
the new shape begin, even when a child ID is reused; old impulses are not reused.

## Connect two bodies by distance

`create_distance_constraint(first, second, settings)` connects two local
anchors in the same world. `DistanceConstraint3DSettings(length)` initially
sets an exact length; its `minimum_length` and `maximum_length` fields also
allow a range. Lengths must be finite, non-negative, and ordered. At least one
body must be dynamic; a fixed body can anchor the constraint to the world.
Active constraints share velocity iterations with contacts. At zero frequency,
they also correct position error directly.

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

`spring_hertz` sets a distance spring frequency in hertz; zero retains the
rigid constraint. `spring_damping_ratio` is zero for weak damping, one for
critical damping, and may exceed one. Both values must be finite and
non-negative. The spring can act on an exact length or the boundaries of a
range; within a range it is inactive. Direct rigid position correction is
disabled while the spring is active to preserve its elasticity. For example:

```silex
var settings = Physics.DistanceConstraint3DSettings(2.0)
settings.spring_hertz = 2.0
settings.spring_damping_ratio = 0.7
var tether = world.create_distance_constraint(anchor, weight, settings)
tether.set_spring(3.0, 1.0)
```

`first_local_anchor` and `second_local_anchor` position the attachment points
in each body's local frame. `current_length()` measures their world-space
separation. `reaction_force()` reports the force applied to the second body
during the last positive step, in mass × distance / second²; it is zero for an
inactive constraint or a step with no impulse. `set_limits(minimum, maximum)`,
`set_spring(hertz, damping_ratio)`, and `set_enabled(enabled)` wake both bodies
and clear the previous reaction.
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
to be delivered. Very fast motion can still cross an obstacle when continuous
collision is disabled, which is the default.

## Query bodies in the world

`ray_cast(ray, ignore_body, filter)` returns the nearest `Ray3D` hit or `null`.
`write_ray_hits(ray, output, ignore_body, filter)` fills a reusable array with one
hit per body, ordered by increasing fraction. For a compound, that hit comes
from its nearest child; `child_id()` gives its ID and is `-1` for a primitive.
Each `WorldRayHit3D` also exposes `body()`, `point()`, `normal()`, and a
`fraction()` between 0 and 1.

`write_overlaps(query, output, ignore_body, filter)` selects bodies overlapping a
`ShapePlacement3D`. Each `WorldOverlap3D` provides `body()`,
`query_child_id()`, and `body_child_id()`; results follow world slot order.
Disabled bodies are excluded from both queries. The optional `ignore_body`
excludes a live body from the same world, such as the ray's emitter. A foreign
or destroyed body is rejected.

Copied points, normals, fractions, and IDs remain readable after later steps
or destruction. The `body()` handle keeps its identity, but `is_valid()`
becomes false when that body or its world is destroyed. The optional
`QueryFilter3D` selects categories through `mask_bits` and includes sensors by
default; `include_sensors:false` excludes them. A body's contact mask does not
affect queries, and queries do not change contacts.

## Linear continuous collision

`RigidBody3DSettings.continuous_collision = true` enables a sweep for a dynamic
body during each positive step; fixed or kinematic bodies with this setting
are rejected. `set_continuous_collision` changes it at
runtime. It is disabled by default. The world finds the first impact along
relative translation before building contacts. A fast body can therefore
reach a thin wall instead of crossing it. Pair filters also apply to the
sweep. Fixed, kinematic, and dynamic targets take part, and the usual contact
solver responds afterward. A pair already overlapping at the start of a step
uses the ordinary discrete response.

When a sensor is crossed completely within one step, the world emits a
transient begin and end in that step, without persistent contact or physical
response. This is an explicit policy difference: the pinned Jolt witness
reports no event for this fast crossing, while the engines agree on a slow
traversal.

The sweep considers translations with start-of-step orientations. It does not
guarantee an impact caused only by fast rotation or exact timing for multiple
successive impacts in one step. Rotation, grazing contacts, and interactions
between multiple continuous bodies still need qualification. The impact time
places the first contact; the solver does not replay the remaining step time
after that impact.

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

Each `RigidBody3DSettings` accepts `collision_filter` and `is_sensor`.
`CollisionFilter3D(category_bits, mask_bits, group_index)` requires at least
one category bit. Two bodies interact when each mask accepts the other's
category. Matching nonzero group indices override masks: positive allows the
pair, negative prevents it. `set_collision_filter` and `set_sensor` take
effect on the next positive step. Sensors report overlap without impulse or
position correction; `Contact3D.is_sensor()` identifies them and their
manifold is empty. Changing sensor mode ends the old pair and begins a new
one on the next step. Sensor contacts do not connect sleep islands.

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
is only optional linear CCD and no static friction guarantee.
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
