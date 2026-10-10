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
efforts, configure the joint motors. An arbitrary pose can exceed their
limits or separate their anchors; the solver resumes resolving them at the
next positive step.

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
This foundation does not yet establish general qualification for ragdoll
falls with contacts or motorized poses.
