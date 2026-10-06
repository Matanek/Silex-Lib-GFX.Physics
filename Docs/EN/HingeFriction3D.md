# Brake a freely rotating hinge

`maximum_friction_torque` opposes relative hinge rotation with bounded torque
when no motor is installed. It slows motion to rest and can hold a load
below its capacity. Zero leaves the axis free.

## Slow down, release and then drive

This wheel starts at 1 rad/s without gravity, with inertia 0.1 kg·m².
A friction torque of 0.1 N·m stops it in one second. The program then
releases the brake, installs a motor and hands control back to friction.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) { var i = 0; while i < count { world.step(1.0/60.0); i++ } }
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed)
    var wheel = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var hinge = world.create_hinge_constraint(pivot,wheel,
        Physics.HingeConstraint3DSettings() ..maximum_friction_torque = 0.1)
    wheel.set_angular_velocity(Math.Vec3(0.0,0.0,1.0)); steps(world,90)
    assert(Math.abs(hinge.angular_speed())<0.00001)
    hinge.set_maximum_friction_torque(0.0)
    wheel.set_angular_velocity(Math.Vec3(0.0,0.0,-1.0)); steps(world,30)
    assert(Math.abs(hinge.angular_speed()+1.0)<0.00001 && hinge.friction_torque()==0.0)
    hinge.set_maximum_friction_torque(0.2)
    hinge.set_motor(Physics.HingeMotor3D(0.5,1.0)); steps(world,60)
    assert(Math.abs(hinge.angular_speed()-0.5)<0.00001 && hinge.friction_torque()==0.0)
    hinge.set_motor(null); steps(world,60)
    assert(Math.abs(hinge.angular_speed())<0.00001 && hinge.motor_torque()==0.0)
}
```

`HingeConstraint3DSettings.maximum_friction_torque` configures the brake at
creation. `set_maximum_friction_torque(torque)` changes it during simulation;
`maximum_friction_torque()` returns its configured capacity. Torque is in
N·m, finite and nonnegative. Negative or nonfinite values are rejected.

## Choose between friction and a motor

Friction is passive: it acts when `hinge.motor() == null`. An installed
motor takes precedence, whether targeting speed or angle, even with zero
maximum torque. Friction capacity is retained; `set_motor(null)` reactivates
it. Set that capacity to zero to leave the axis free without a motor.

The brake applies at most its torque capacity during each step. It reduces
relative speed without returning to an initial angle. It also supplies the
reaction needed to hold a stationary load below its capacity. A greater
load makes it slip. It is neither viscous damping proportional to speed
nor an angle lock.

## Measure and change

`friction_torque()` measures signed torque applied to the second body during
the last positive step; the first receives the opposite. Its value stays
bounded by configured capacity and is zero while a motor takes precedence.
`motor_torque()` remains reserved for motor effort. `reaction_torque()`
includes friction, axis and stop reactions.

Changing capacity wakes the bodies and clears reactions, like other hinge
mutations. A zero step preserves measurements. Passive friction permits
sleep at rest; disabling a body or the hinge suspends its effort. Stale
and orphan handles follow the [hinge guards](Hinge3D.md).

An offset pivot, mass, center of mass and inertia determine the response.
Friction, contacts and other constraints share the same world. See
[position control](HingePosition3D.md) to target an angle and the
[hinge guide](Hinge3D.md) for frames and hard stops.
