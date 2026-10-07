# Drive a hinge towards an angle

`HingeMotor3D.position(angle, maximum_torque, stiffness, damping)` approaches
a signed angle through a damped spring. The hinge retains its anchor and axis;
its motor supplies bounded torque. The `HingeMotor3D(speed, maximum_torque)`
constructor retains velocity control.

## Reach and change the target

This recipe uses a fixed pivot, a free body without gravity, and a damped servo.
It then reverses the target, switches to velocity control and leaves the body
rotating with no motor.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) {
    var index = 0; while index < count { world.step(1.0/60.0); index++ }
}
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,body,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D.position(0.75,10.0,1.6,0.8))
    steps(world,180)
    assert(Math.abs(hinge.angle()-0.75) < 0.001)
    hinge.set_motor(Physics.HingeMotor3D.position(-0.75,10.0,1.6,0.8))
    assert(hinge.motor_torque()==0.0)
    steps(world,180)
    assert(Math.abs(hinge.angle()+0.75) < 0.001)
    hinge.set_motor(Physics.HingeMotor3D(0.5,1.0))
    steps(world,30)
    assert(Math.abs(hinge.angular_speed()-0.5) < 0.00001)
    hinge.set_motor(null)
    steps(world,30)
    assert(Math.abs(hinge.angular_speed()-0.5) < 0.00001)
}
```

`angle` is in radians, within `[-pi, pi]`, using the sign of `hinge.angle()`.
The motor takes the shortest angular path. Current limits clamp the effective
target; `motor.target_angle` retains the requested angle. Changing limits
therefore reevaluates the target without reinstalling the motor.

## Set effort and response

In the symmetric form, `maximum_torque` is finite and nonnegative, in N·m. The bound applies to the
accumulated motor torque of the step. Zero leaves the axis free, like an absent
motor; it does not act as a rigid brake.

`stiffness` is finite and strictly positive, in N·m/rad; `damping` is finite
and nonnegative, in N·m·s/rad. Low damping allows oscillations and target
overshoot. Torque follows the implicit spring; no rigid displacement projects
the angle straight onto the target. At finite time steps, integration adds
numerical damping even with `damping:0.0`.

Under constant load, a servo can remain offset from its target: the spring
balances external torque. An insufficient torque bound can prevent reaching
that equilibrium. Explicit stiffness and damping retain their units when
inertia, mass or the anchor changes.

The `hinge.motor()` snapshot identifies a servo through a present
`target_angle`; it also carries `stiffness` and `damping`. In velocity mode,
the angle is absent and these coefficients are zero; `speed` remains the
signed velocity target. With `position`, `speed` is zero. [Combined control](HingeCombined3D.md) also supplies a velocity.

## Change and observe

`set_motor` replaces the complete intent, wakes the bodies and resets reactions.
It changes the target, coefficients, bound or mode. `null` turns off the motor;
anchors, axes and stops remain active. `motor_torque()` measures signed motor
torque applied to the second body during the last step; the first receives
the opposite. `reaction_torque()` also includes axis and stop reactions.
A zero time step preserves these measurements. Stale or orphan handles follow
the [hinge guards](Hinge3D.md).

A unilateral hard stop arrests velocities that would cross it; existing penetration is
corrected in the pose. Narrowed limits and the servo share the real world,
its contacts and safety; pose recovery does not supply new momentum.

The [axis brake](HingeFriction3D.md) acts when the motor is absent. [Signed
bounds](HingeTorqueBounds3D.md) permit different effort in each direction. [Soft stops](HingeSoftLimits3D.md) allow damped deflection.
For velocity control, see the [hinge motor](Hinge3D.md#request-a-speed-with-a-maximum-torque).
