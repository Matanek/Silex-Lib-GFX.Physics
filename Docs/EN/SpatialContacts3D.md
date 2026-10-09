# Bring a spatial chain into contact with a plane

The [chain with two perpendicular hinges](SpatialHinges3D.md) can carry a
spherical payload to a horizontal plane, then release the contact when its
motor reverses. Joint reactions and contact impulse support the load together.

The [executable consumer](../../Tests/Consumer/Tests/SpatialContacts3D.sx)
checks the path with and without the plane from the workspace root:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialContacts3D.sx
```

## Arrange the contact

Bodies, Z/X axes, anchors, masses and inertias follow the spatial recipe.
The payload is a sphere of radius 0.15 m, initially centered at `(1,0,±0.8)`.
A fixed body carries `Shape3D.plane(Plane3D(Vec3(0,1,0),-0.22))`: its plane
lies at Y=−0.22 m. Disable pivot and arm collisions; keep payload collisions
active. Both surfaces have zero friction and restitution. Motors have
60/40 N·m capacities: the first holds the arm, the second drives at
±0.2 rad/s, reverses after 2/3 s and brakes after 4/3 s.

## Include the application point

After `World3D.step`, `write_contacts` returns snapshots of the last step.
Their normal points from the first body to the second. The impulse
`normal * normal_impulse + tangent_impulse` applies to the second; negate
it for the first. `write_points` returns each manifold point's position and
impulses. For multiple points, sum individual moments instead of multiplying
the average point by the total impulse.

The linear balance adds the contact impulse. The spin balance adds
`contact_lever.cross(impulse)` about the center of mass at application time.
The total angular momentum balance adds `point.position.cross(impulse)`
about the world origin. Hinge forces and torques keep
[their conventions](SpatialHinges3D.md).

In this Silex recipe, the sphere-plane point is rebuilt on the sphere center's
normal: its lever is `(0,-radius-separation/2,0)` and the frictionless impulse
creates no spin. Its public position is still needed for total angular
momentum. This reconstruction depends on this shape and plane; end-of-step
poses may already include corrections. A contact cached by another engine
may have a slightly offset lever: do not assume a central impulse when
comparing engines.

## Verified scope

Two masses, two offsets ±0.8 m, 60/120 Hz and plane presence/absence yield
16 two-second paths. Silex and pinned Jolt pass in Native Debug/Release on
macOS ARM64. With the plane, peak impulse exceeds 0.1 N·s; the motor reverses
and contact releases before final rest. Excursion exceeds 0.07 rad and both
speed directions exceed 0.15 rad/s.

Bounds are 1e−5 N·s for linear balance, 0.001 N·m·s for spin, 0.003 per step
and 0.03 cumulatively for total angular momentum. Anchors and axes stay below
0.005 m/rad, penetration below 0.003 m and root angle below 0.02 rad. Final
speeds stay below 0.005 m/s or rad/s; weight/torque errors below 0.05 N/N·m.
Motor capacities and projections are checked.

Silex publishes solved impulses. The Jolt oracle infers normal impulse from
the payload's linear balance and observes the pre-solve point through its
listener; this inference does not independently prove normal balance or
contact moment. Bounds include integration and pose corrections, without
exact discrete conservation or phase/cost parity. This recipe does not
qualify friction, stops, sleep, large rotations, anisotropic inertia,
multiple contacts or arbitrary chains.
