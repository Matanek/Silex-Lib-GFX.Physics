# Drive with different torque in each direction

`HingeMotor3D(speed, minimum_torque, maximum_torque)` bounds motor effort
between two signed torques in N·m. This example accelerates toward +1 rad/s
with 0.1 N·m, then reverses the target with only −0.025 N·m: rotation stays
positive during the slower braking. The two-argument constructor retains
symmetric capacity in both directions.

```sx
use GFX.Physics
use STD.Math

func steps(world:Physics.World3D, count:int) {
    var i = 0; while i < count { world.step(1.0/60.0); i++ }
}
func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,body,Physics.HingeConstraint3DSettings()
        ..motor = Physics.HingeMotor3D(speed:1.0,minimum_torque:-0.025,maximum_torque:0.1))
    steps(world,60);assert(Math.abs(hinge.angular_speed()-1.0)<0.0001)
    hinge.set_motor(Physics.HingeMotor3D(speed:-1.0,minimum_torque:-0.025,maximum_torque:0.1))
    steps(world,60);assert(Math.abs(hinge.angular_speed()-0.75)<0.0001)
    hinge.set_motor(Physics.HingeMotor3D.position(angle:-0.5,minimum_torque:-0.2,maximum_torque:0.1,
        stiffness:1.6,damping:0.8))
    steps(world,360);assert(Math.abs(hinge.angle()+0.5)<0.02)
    hinge.set_motor(Physics.HingeMotor3D(1.0,0.2))
    assert(hinge.motor()!.minimum_torque == -0.2 && hinge.motor()!.maximum_torque == 0.2)
}
```

The servo also accepts `HingeMotor3D.position(angle, minimum_torque,
maximum_torque, stiffness, damping)`. It retains the units and implicit
spring of [position control](HingePosition3D.md).

## Choose the signed interval

The sign follows `angular_speed()`: positive torque tends to increase the
second body's rotation relative to the first around the first body's axis.
The first receives the opposite effort. Both bounds must be finite and
ordered; they may be equal and the interval does not have to contain zero.

| Interval | Permitted effort |
|---|---|
| `[-0.2, 0.2]` | Symmetric capacity |
| `[-0.025, 0.1]` | Negative effort four times weaker |
| `[0.0, 0.1]` | Positive torque only; cannot brake positive rotation |
| `[0.03, 0.08]` | Continuous positive effort, even at the target |
| `[-0.02, -0.02]` | Prescribed negative torque |
| `[0.0, 0.0]` | No motor effort |

A torque bound does not prohibit an existing direction of rotation. With
capacity in only one direction, the motor may not reach its target. An
interval excluding zero imposes its bound closest to zero whenever the
command requests less effort, including a zero target. Consider that
continuous action before selecting such bounds.

## Replace and observe the motor

`set_motor` replaces target, bounds and mode together, wakes the bodies and
clears reactions. The `motor()` snapshot exposes `minimum_torque` and
`maximum_torque` as immutable signed bounds. Existing symmetric forms give
`minimum_torque == -maximum_torque`; their capacity argument remains
nonnegative.

`motor_torque()` measures signed torque during the last step in which the
motor acts on active bodies, within the configured interval. Before the
first step, after mutation or during suspension, the observation is zero
even when the interval excludes zero. Capacity is not multiplied by the iteration count.
`reaction_torque()` also includes axis and stop reactions; stops may oppose
the motor and arrest motion. A zero step preserves observations. Mutation,
suspension, destruction and orphaned handles follow the [hinge](Hinge3D.md).

An installed motor, including one with no effort, retains priority over
[passive friction](HingeFriction3D.md). `set_motor(null)` removes it. Soft
stops and combined position/velocity control remain to be qualified.
