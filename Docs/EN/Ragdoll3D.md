# Create a ragdoll assembly and manipulate its pose

`Ragdoll3DSettings` describes a reusable hierarchy of bodies connected by
[swing/twist](SwingTwist3D.md) joints. `World3D.create_ragdoll` creates an
independent instance; `destroy_ragdoll` destroys its bodies and their joints.
The [public consumer](../../Tests/Consumer/Tests/Ragdoll3D.sx) demonstrates
poses, offset mass centers and multiple instances.

## Describe the parts at rest

This fragment creates a three-part chain in an existing `world`:

```sx
let body = Physics.RigidBody3DSettings()
var settings = Physics.Ragdoll3DSettings([
    Physics.RagdollPart3D(-1, body),
    Physics.RagdollPart3D(0, body,
        local_transform:Physics.Transform3D(Math.Vec3(1.0, 0.0, 0.0))),
    Physics.RagdollPart3D(1, body,
        local_transform:Physics.Transform3D(Math.Vec3(0.0, 2.0, 0.0)))
])
var ragdoll = world.create_ragdoll(settings,
    Physics.Transform3D(Math.Vec3(0.0, 10.0, 0.0)))
```

The first part is the only root (`parent = -1`). Each subsequent part names
a parent already present in the array. `local_transform` places its joint
frame relative to its parent; the root frame is relative to the placement
passed at creation. The settings copy the initial array.

`body_offset` places the shape origin relative to the joint frame. It can
include translation and rotation. The mass center retains its own offset in
the body settings. `body.transform` must remain identity: assembly placement
and `body_offset` own that responsibility.

The child part's `joint` field configures its limits, friction and motors.
Both local joint frames must remain identity: the assembly derives them from
the rest pose and body offsets, with zero relative angle at rest. Each joint
must include at least one dynamic body. The root has no parent joint.

## Read and impose a pose

`write_pose(output)` replaces the output array with world joint frames in
part order. `write_local_pose(output)` keeps the root **in world coordinates**
and expresses every other part relative to its parent. Both exclude shape
offsets; `body(index).transform()` reads the world shape pose.

`set_pose(pose, reset_velocity:true)` and `set_local_pose(pose,
reset_velocity:true)` require exactly one transform per part, following the
same conventions as the readers. Imposing a pose clears kinematic targets,
joint reactions and cached impulses for the assembly, then wakes the world.
By default it zeros linear and angular velocities; `reset_velocity:false`
preserves them. Already applied forces remain.

An imposed pose is an immediate placement. To follow a target with physical
efforts, use the motorized pose commands below. An arbitrary pose can exceed their
limits or separate their anchors; the solver resumes resolving them at the
next positive step.

## Move a pose and resume simulation

`move_to_pose(pose, duration)` and `move_to_local_pose(pose, duration)` use
the same frames as the pose readers. They copy the target and set each member’s
velocities to reach it progressively, without immediate placement. Duration
must be finite and strictly positive. Dynamic members become kinematic: they
push external bodies through contact, without receiving recoil or gravity.
A new call replaces the movement from the current pose. One call per target
is sufficient.

In this fragment, `desired_pose` contains one world joint transform per member;
steps run in the application’s physics loop:

```sx
ragdoll.move_to_pose(desired_pose, 1.0)
world.step(0.25)
ragdoll.resume_simulation()
```

`resume_simulation()` returns originally dynamic members to simulation with
their masses, inertias and current velocities. Their poses and handles remain
unchanged; their kinematic target is cancelled. Releasing during movement
preserves its velocity. A reached target stands still: releasing after it has
stopped starts with zero velocity. Originally kinematic members retain their
type and command; fixed bodies remain fixed and a target attempting to move
them is rejected. Repeating the release has no effect.

Transitions preserve filters, limits and configured motors while resetting
cached reactions. Entering kinematic motion also clears accumulated forces
and torques. To resume motor tracking, call `resume_simulation()` followed by
`drive_to_pose` or `drive_to_local_pose`. `set_pose` preserves the current mode
while cancelling pending movement.

Velocities are computed at each center of mass, including body offsets and
rotations. Moving individual members does not replace skeleton interpolation:
provide coherent poses so that anchors and limits remain compatible when
released. Constraints do not correct two kinematic members relative to each
other. The [public consumer](../../Tests/Consumer/Tests/RagdollKinematic3D.sx)
exercises rotated frames, offset centers, replacement targets, fixed roots,
external contact, release and independent instances.

## Follow a pose with motors

`drive_to_pose(pose, maximum_torque, stiffness, damping)` and
`drive_to_local_pose(pose, maximum_torque, stiffness, damping)` use the world and
local reading conventions. The array must contain one transform per part.
Only relative child rotations become targets: the root's world position and
rotation, and all translations, command no displacement. Physical anchors keep
the bodies connected.

The call replaces each joint's twist and swing motors, wakes the bodies and
clears stored reactions. It preserves their poses, velocities, limits, friction
and collision filters. The solver clamps targets to the existing joint limits.
Body offsets and the joints' current frames participate in rotation conversion.
Values are copied: later changes to the array do not change the target.

`maximum_torque` is a finite, nonnegative torque in N·m **per axis**;
`stiffness` is finite, strictly positive stiffness in N·m/rad, and `damping`
is finite, nonnegative damping in N·m·s/rad. A finite spring under gravity can
retain an offset from the target. Supply a new pose when the target changes;
no update on every frame is required.

`stop_motors()` removes both motors from every joint. It preserves poses and
velocities, leaving gravity, limits, friction and collisions active. It does
not restore a motor configuration that preceded the pose command.
The [public test](../../Tests/Consumer/Tests/RagdollMotors3D.sx) exercises these
calls, independent instances, changed frames and saturation at joint limits.

## Collisions and lifetime

Direct parent/child parts do not collide. Other parts in the same instance
follow their ordinary filters; `self_collision:false` suppresses all internal
collisions. Two instances remain distinct even when they share settings.
This filtering also applies to sensors and continuous collision and combines
with `CollisionFilter3D`. Geometric queries still use their own query filter.

`body(index)` accesses the body; `joint(index)` accesses its parent joint,
or returns `null` for the root. Destroying any one of these objects separately
invalidates the assembly (`is_valid() == false`). `destroy_ragdoll` can still
clean up its remaining bodies; a second call is an error. World destruction
also invalidates the assembly and all its handles, without those handles
retaining the world.

## Qualification

Tests cover noncommuting rotations, mass offsets, poses, filtering, stale
handles and free fall at 60/120 Hz. The pinned Jolt witness compares
`Ragdoll.GetPose/SetPose` after explicit conversion between body origins and
joint frames, plus allowed pairs within and across instances, in Debug/Release.
A free three-sphere chain is also qualified against Jolt: an off-center impulse
on the last member without gravity, transmission to the parent, bounded momentum
balances and anchors; then symmetric fall onto a frictionless floor until rest,
at 60/120 Hz in Debug/Release. Transient floor crossing is bounded separately
from final height. These passive recipes do not yet establish general
qualification for ragdoll impacts or active limits.

A fixed-root chain with two offset spheres also tracks opposing targets, returns
to neutral and becomes passive under gravity, at 60/120 Hz in Debug/Release.
Geometric conventions, bounded torques and settled poses are compared with
Jolt `Ragdoll.DriveToPoseUsingMotors`. This contact-free recipe does not qualify
arbitrary trajectories or motorized impacts.

A [passive chain with stops](../../Tests/Consumer/Tests/RagdollLimits3D.sx)
also transmits opposed angular impulses through two twist joints bounded at
−0.2/+0.35 rad, with locked swing. At 60/120 Hz and in two world orientations,
angular momentum is conserved and stops do not create kinetic energy. Anchors,
transmission to parents and settled angles/velocities are qualified against
the native Jolt ragdoll in Debug/Release. Observations immediately before/after
an impulse verify that it changes velocity without placing bodies. This recipe
has neither gravity nor contacts; it does not qualify combined swing impacts.

An [offset sphere member with a fixed root](../../Tests/Consumer/Tests/RagdollContact3D.sx)
also combines swing/twist targets outside the limits with a frictionless floor.
The member presses on the floor, lifts, returns, then becomes passive with an
angular impulse. The witness without a floor separates stops from contact,
at 60/120 Hz, in two horizontal orientations and both lateral signs. Geometry,
torques, penetration and linear momentum balances are checked every step.
In contact windows, an angular momentum balance projected onto the floor
tilt axis also independently checks the vertical force.
Established poses and mean velocities/forces over half-second windows are
compared with native Jolt ragdolls in Debug/Release. Jolt penetration slop is
explicitly set to 1e−6 m; its normal force is inferred from the linear balance,
while Silex exposes the measured impulse. Simultaneous stops produce stepwise
velocity/force variations in Jolt: instantaneous equality is not qualified.
Window-mean equilibria do not establish impact trajectories or general
motorized chains with several free members.

The [free chain with combined limits](../../Tests/Consumer/Tests/RagdollCombinedLimits3D.sx)
exercises two joints with a 0.3/0.45 rad elliptical cone and −0.2/+0.35 rad
twist stops. An oblique angular impulse followed by its opposite on the leaf
reaches the stops and transmits motion to the parents. Without gravity or
contact, global linear momentum, angular momentum, center of mass and energy
remain within their numerical budgets. The native Jolt witness compares these
balances and mean energy over two fixed windows at 60/120 Hz, in two world
orientations and both signs, in Debug/Release. Commands do not place any member.
This proves passive limits on a free chain, without establishing equal poses
at every impact or general composition with a floor.

The [mobile two-motor chain on the floor](../../Tests/Consumer/Tests/RagdollMobileContact3D.sx)
combines three free spheres, two opposing swing targets beyond their cone
and a frictionless floor. A declared uniform vertical impulse makes the
chain leave and return to the floor; commands preserve poses and velocities.
Anchors, limits, motor budgets, linear balances and angular momentum are
checked at every step. Established geometry and window-mean efforts and
velocities are compared with the Jolt ragdoll at 60/120 Hz, two signs and
two world orientations, in Debug/Release.

This case selects `velocity_iterations = 48` and `position_iterations = 16`;
the defaults remain 12 and 4. The default velocity budget does not meet the
1 N mean reaction bound for this recipe even when positions are close.
Jolt uses 24 velocity iterations, 16 position iterations and 1e−6 m
penetration slop. These counts do not represent identical algorithmic work.
Jolt's normal impulse is inferred from the linear balance; Silex exposes the
measured impulse. Instantaneous force parity and arbitrary impact trajectories
remain unqualified.

A [spatial two-motor chain](../../Tests/Consumer/Tests/RagdollSpatialContact3D.sx)
places three moving spheres on triangular supports, with the second constraint
frame rotated by 0.6 rad. Targets combine swing on two axes and twist; an
oblique impulse on the leaf accompanies floor departure and return. At 60/120 Hz,
both signs and two world orientations, frames, anchors, torques, limits, contacts
and balances are checked. Constraint orientations, centered geometry and mean
angular velocity/reaction vectors expressed in the root body's frame are
compared with Jolt in Debug/Release on macOS ARM64. Settings remain 48/16 for
Silex and 24/16 for Jolt; existing worlds and demos retain their budgets.

This witness checks intrinsic angular momentum around the center of mass and
the global Y component throughout the run. Vertical contact projection also
moves the orbital contribution about a fixed origin when the group has horizontal
momentum: that orbital balance at impacts is not declared equivalent. The test
does not establish general impact trajectories or comparable performance. An
initially collinear support exhibits slow motion in both engines that invalidates
the resting windows; the published qualification covers the declared triangular
support. The public consumer also checks an independent instance and destruction/
recreation.

The `RagdollKinematic` witness compares kinematic driving with Jolt at 60/120 Hz
in Debug/Release on macOS ARM64: three offset members, rotation/translation,
release during movement and pushing an external sphere. Centers, rotations and
velocities are checked analytically and compared at five fixed times. Silex’s
scheduled stop is reproduced by explicitly stopping the Jolt witness. Initial
contact timing and instantaneous impulses are not compared.
