# Cushion a hinge stop

`limit_spring` allows an angular stop to yield temporarily under load and
return with a damped response. A hinge without a spring retains its rigid
stops. This example holds an arm against a soft stop with different motor
effort in each direction.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var arm = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,arm,Physics.HingeConstraint3DSettings()
        ..minimum_angle = -0.3 ..maximum_angle = 0.3
        ..limit_spring = Physics.HingeLimitSpring3D(stiffness:1.6,damping:0.8)
        ..motor = Physics.HingeMotor3D(speed:1.0,minimum_torque:-0.1,maximum_torque:0.2))
    var step = 0;while step<360 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()-0.425)<0.003)
    assert(Math.abs(hinge.limit_torque()+0.2)<0.001)
    hinge.set_motor(Physics.HingeMotor3D(-1.0,-0.1,0.2))
    step = 0;while step<360 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()+0.3625)<0.003)
    hinge.set_limit_spring(null)
    step = 0;while step<60 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()+0.3)<0.003)
}
```

The positive motor supplies 0.2 N·m at equilibrium. With stiffness of
1.6 N·m/rad, the stop deflects by 0.125 rad: the arm settles near 0.425 rad
although its nominal upper bound is 0.3. After reversal, negative effort of
0.1 N·m causes 0.0625 rad of deflection. Removing the spring restores the
rigid response at the same bounds.

## Choose the response

| Parameter or measurement | Meaning |
|---|---|
| `HingeLimitSpring3D(stiffness, damping)` | Immutable stop spring value |
| `stiffness` | Strictly positive stiffness, in N·m/rad |
| `damping` | Nonnegative damping, in N·m·s/rad |
| `limit_spring = null` | Rigid stops, the default |
| `limit_torque()` | Signed stop torque from the last step, in N·m |

The spring acts when the angle reaches or exceeds a bound, using the initial
state of the step. Crossing from inside activates it on the following step;
pose is not projected onto a soft stop. For an interval, the lower stop pushes
in the positive direction and the upper stop in the negative direction.
A stop does not pull an arm returning into the interval: it rotates freely
and may reach the opposite stop. Equal bounds create a bilateral angular
spring that can oscillate around their angle. The angle stays signed in
[-π, π]; the spring selects the closest bound on the circle and does not
count turns. The full [-π, π] interval stays free.

Zero damping still retains numerical damping from integration. Mass, inertia
and pivot offset change the transient response; stiffness remains in physical
units. Motor torque bounds do not bound the spring torque. The
[position servo](HingePosition3D.md) retains its target clamped to the nominal
interval; [friction](HingeFriction3D.md) stays passive and stops acting while
a motor is installed.

## Modify and measure

`set_limit_spring(Physics.HingeLimitSpring3D(...))` replaces the spring;
`set_limit_spring(null)` restores rigid stops. A change clears previous
reactions and wakes the linked bodies, as do `set_limits`, `set_anchors`
and `set_frames`. `limit_spring()` returns the selected snapshot.
The value rejects NaN, infinity, zero/negative stiffness and negative damping.

`limit_torque()` separates the stops from the motor and friction;
`reaction_torque()` includes their total effort and alignment reactions.
Changing a body's pose or mass retains the last step's measurement until the
next step, whose solve uses the new mobility. A zero step retains observations. A disabled hinge or disabled body produces
zero measurements after the next positive step. Destruction
and validity follow the [hinge](Hinge3D.md) rules.

Qualification covers both directions, free interior motion, oscillations,
equal bounds, two inertias, an offset pivot, mutations, motors, friction and
a loaded chain within its plane with real contacts. Trajectories and efforts
are compared against Jolt in Native Debug/Release on macOS ARM64. General
spatial chains are not qualified by this evidence.
