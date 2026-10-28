# 3D swing and twist

`World3D.create_swing_twist_constraint` keeps two attachments together, limits
twist about X and swing about Y/Z. The two drives can be enabled independently.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var support=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type=Physics.BodyType3D.fixed ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var body=world.create_rigid_body(Physics.RigidBody3DSettings()
        ..allow_sleep=false ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var joint=world.create_swing_twist_constraint(support,body,
        Physics.SwingTwistConstraint3DSettings() ..swing_limits=Physics.SwingLimits3D.cone(Math.Vec2(0.3,0.6))
        ..minimum_twist=-0.4 ..maximum_twist=0.4
        ..twist_motor=Physics.TwistMotor3D.position(0.2,5.0,2.0,1.0))
    var i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.twist_angle()-0.2)<0.002 && joint.anchor_error().length()<0.001)
    joint.set_twist_motor(null)
    joint.set_swing_motor(Physics.SwingMotor3D.position(Math.Vec2(0.2,0.0),5.0,2.0,1.0))
    i=0;while i<240 { world.step(1.0/60.0);i++ }
    assert(Math.abs(joint.swing_angles().x-0.2)<0.002)
    world.destroy_swing_twist_constraint(joint);assert(!joint.is_valid())
    print("swing twist recipe: ok")
}
```

## Frames and limits

`first_local_frame` and `second_local_frame` are local to each body's shape
frame. Their origins are the anchors; their rotations define X for twist and
Y/Z for swing. `orientation()` is the second frame relative to the first,
decomposed as swing followed by twist. `twist_angle()` is signed in [−π, π].
`swing_angles()` contains `2 atan2(q.y, q.w)` and `2 atan2(q.z, q.w)` from the
swing quaternion, rather than Euler angles. At 180° swing, twist is singular;
the decomposition then chooses zero twist.

`SwingLimits3D.cone(half_angles)` bounds swing by an ellipse in quaternion Y/Z
space, with radii `sin(half_angles.x/2)` and `sin(half_angles.y/2)`. Half-angles
lie in [0, π]: zero locks a direction and π releases it.
`pyramid(minimum, maximum)` bounds both swing angles by a rectangle. Finite
ordered bounds lie in [−π, π], may be asymmetric and may exclude zero.
Equal bounds lock the corresponding angle. Local frames define the reference
orientation.
Twist limits are finite and ordered in [−π, π]; equal limits lock twist.
All rotations are free by default.

## Drives and friction

`TwistMotor3D(speed, maximum_torque)` and `SwingMotor3D(speed, maximum_torque)`
command scalar or Y/Z angular velocity in rad/s. Components are carried by the
second constraint frame; during combined rotations they are not the derivatives
of the displayed swing angles. Overloads with `minimum_torque, maximum_torque`
provide signed bounds in N·m. The swing budget applies independently to Y and Z.

`position` and `position_and_velocity` factories add targets in radians,
stiffness in N·m/rad and damping in N·m·s/rad. Targets are projected onto
admissible limits, using Euclidean projection onto the quaternion ellipse
for cones. A part without a position drive keeps its current orientation in
the composed target. Servo errors use the closest quaternion and the angular
approximation `2 sin(θ/2)`.

`maximum_friction_torque` brakes each unpowered direction without injecting
energy. A present motor with zero capacity replaces friction on its directions;
`null` restores passive behavior. Friction and motor budgets default to zero.

## Observation, mutation and lifetime

`angular_speed()` expresses relative velocity in the current second frame.
`motor_torque()` and `friction_torque()` contain X/Y/Z components in the motor
axes of the last positive step. `reaction_force()` and `reaction_torque()` are
the world-space force in N and free torque in N·m on the second body; torque
excludes the moment of anchor force. `anchor_error()` points from the first
anchor to the second in meters. A zero step preserves reactions.

`set_frames`, `set_anchors`, `set_swing_limits`, `set_twist_limits`, both
`set_*_motor`, `set_maximum_friction_torque` and `set_enabled` clear reactions
and wake linked bodies. Disabling either body or the joint suspends solving.
Creation requires distinct bodies in the same world with at least one dynamic
body. Explicit removal or destruction of either body or the world invalidates
the handle; only `is_valid()` can then read it.

## Stop correction and an offset anchor

Position correction at a stop accounts for the coupling between rotation and
anchor displacement. It preserves the attachment during angular correction;
the following point projection must not undo that correction. SixDOF angular
correction retains its free translations and does not implicitly fix an anchor.

The [offset-anchor consumer](../../Tests/Consumer/Tests/OffsetLimitProjection3D.sx)
checks an initial 0.3 rad violation: the residual stays below 0.2 rad with one
position pass, attachment error below 10 µm, and the total center of mass is
preserved when both bodies move. Both stops, two world frames and 60/120 Hz steps
are covered; a SixDOF countercheck verifies that no translation is imposed.

## Qualification

Headless consumers cover free motion, Y/Z/twist limits, diagonal ellipses,
asymmetric pyramids, locked axes, independent servo recurrences at 60/120 Hz,
friction, signed budgets, frame changes, sleep, contacts and lifetime. The
pinned Jolt witness compares reduced cases in Debug/Release.

The [loaded consumer](../../Tests/Consumer/Tests/LoadedSwingTwist3D.sx) drives
all three axes simultaneously under gravity, with an offset anchor, rotated
frames, 1/2 kg masses and 60/120 Hz steps. Targets reverse and then recenter;
each motor axis remains bounded to 30 N·m. Weight deflects the equilibrium:
a finite-stiffness position target is not a rigid attachment. Vector balances,
anchors and steady states are qualified against Jolt; equal transient responses
are not established. This recipe has no contact or second dynamic articulation.

Reactions are accumulated impulses divided by the step duration. Resolution
uses the anchor before and after pose advancement, so the moment of the total
force cannot be reconstructed exactly with a single initial lever. An exact
local spin balance must separate these phases; the public consumer checks total
angular momentum and static reactions. General spatial chains and exact
impact-step reaction equality remain unqualified.

[Compose a motorized shoulder and elbow](ArticulatedPose3D.md): four servos, transmitted load and moving frames.
