# Follow an angle and a velocity together

`HingeMotor3D.position_and_velocity(angle, speed, maximum_torque, stiffness, damping)`
gives the servo an angle target and a commanded velocity. Update both each
step to follow a trajectory. The six-argument form replaces the symmetric
capacity with `minimum_torque, maximum_torque`.

## Follow a steady rotation

The body starts at 0.5 rad/s and its target advances at that same speed. The
motor maintains tracking without external torque or damping lag.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..angular_velocity = Math.Vec3(0.0,0.0,0.5)
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,body)
    let dt = 1.0/60.0
    var i = 0
    while i<180 {
        let angle = i as float*dt*0.5
        hinge.set_motor(Physics.HingeMotor3D.position_and_velocity(angle,0.5,-1.0,1.0,1.6,0.8))
        world.step(dt)
        assert(Math.abs(hinge.angle()-(angle+dt*0.5))<0.00001)
        assert(Math.abs(hinge.angular_speed()-0.5)<0.00001)
        assert(Math.abs(hinge.motor_torque())<0.00001)
        i++
    }
    assert(hinge.motor()!.speed==0.5 && hinge.motor()!.target_angle!=null)
}
```

Supply the trajectory angle at the beginning of the step. The body reaches
the next step’s angle. The application must update the trajectory itself:
the motor does not automatically advance `target_angle`.

## Choose targets and effort

`angle` is finite within `[-pi, pi]`; `speed` is finite in rad/s. Their signs
follow `hinge.angle()` and `angular_speed()`; angular error uses the short path.
Current limits clamp the effective angle target; the snapshot preserves the
requested angle. Limits do not clamp commanded speed: a stop can supply
the torque opposing the motor.

Stiffness and damping retain the units of the [position servo](HingePosition3D.md).
[Signed torque bounds](HingeTorqueBounds3D.md) constrain the total motor torque
per step, shared across all passes. Zero symmetric capacity leaves the axis free.
Zero commanded velocity exactly reproduces position mode.

Combined mode adds velocity to the implicit spring bias. With a fixed angle
and nonzero velocity, the body therefore settles offset from its target
rather than rotating indefinitely. Without load or stops, at constant step h,
stiffness k and damping c, the equilibrium offset is `(c+h*k)*speed/k`.
This expression includes discretization; contacts and loads change equilibrium.
Use zero velocity to hold a fixed angle precisely.

## Replace and observe

`set_motor` replaces both targets, coefficients and bounds, wakes bodies and
clears reactions. `motor()` preserves immutable `target_angle`, `speed`,
`stiffness`, `damping` and both bounds. `position` still supplies zero velocity;
the velocity constructor still has no angle target.

`motor_torque()` measures the signed torque applied to the second body in the
last step; the first receives its opposite. `reaction_torque()` includes axes
and stops; `limit_torque()` measures stops separately.
A zero step preserves these observations. Mode changes and motor removal follow
the [hinge](Hinge3D.md) rules. An installed motor, even with zero effort,
takes precedence over [passive friction](HingeFriction3D.md).

[Soft stops](HingeSoftLimits3D.md) can deform under combined commands.
Changing mass, center of mass, anchors or frames preserves physical units
but can change transient tracking.
Qualification compares Jolt Debug/Release for fixed and moving targets,
signed saturation, modes, rigid-stop loads, offset pivot, angular seam and
unequal inertias. Rigid impacts differ in activation before/after displacement;
their transient parity is not claimed. Contacts and loaded chains are qualified
in their plane; general spatial chains remain to be extended.
