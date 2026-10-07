# Follow a moving slider target

`SliderMotor3D.position_and_velocity` combines a position in metres with a
signed relative velocity in m/s. Updating both before every step follows a
trajectory with less lag than a position-only servo. Motion follows the first
frame's X axis, as for the slider.

Run the sinusoidal target recipe from the workspace root with
`silex run Packages/GFX.Physics/Tests/Consumer/Smokes/SliderCombinedRecipe3D.sx`.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type = Physics.BodyType3D.fixed
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail,carriage)
    var step = 0
    let dt = 1.0/120.0
    while step<960 {
        let time = step as float*dt
        let position = 0.75*Math.sin(time*0.8)
        let speed = 0.6*Math.cos(time*0.8)
        joint.set_motor(Physics.SliderMotor3D.position_and_velocity(position,speed,20.0,8.0,4.0))
        world.step(dt)
        assert(Math.abs(joint.motor_force())<=20.0001 && joint.anchor_error().length()<0.0001)
        step++
    }
    joint.set_motor(Physics.SliderMotor3D.position_and_velocity(0.5,0.3,-2.0,3.0,8.0,8.0))
    assert(joint.motor()!.speed==0.3 && joint.motor()!.minimum_force== -2.0)
    print("Moving slider target followed with bounded combined position and velocity drive")
}

```

The symmetric 20 N capacity bounds effort over the entire step. The final
command demonstrates signed bounds of −2 N and +3 N. Commands and ordered
bounds must be finite, stiffness positive and finite in N/m, damping
nonnegative and finite in N·s/m. `motor()` retains the requested command;
`motor_force()` measures its signed force.

The target position is clamped to the limits before evaluating the spring,
including [soft stops](SliderSoftLimits3D.md). Velocity remains a command
bias and can compress a soft stop; a rigid stop bounds travel. Zero velocity
reproduces the [position servo](SliderPosition3D.md). Motors take precedence
over passive friction even at zero capacity. `set_motor` replaces the command,
clears reactions and wakes the bodies; `null` restores passive friction.
Suspension, zero steps and destruction follow the [slider](Slider3D.md).

A fixed position target and nonzero velocity produce a shifted equilibrium,
rather than endless travel. Without load or limits, the offset is
`(damping + delta * stiffness) * speed / stiffness` at fixed step `delta`.
A load adds its force/stiffness offset. For a moving target, provide position
and its derivative before each step, as above.

Consumers qualify 60/120 Hz recurrences, zero velocity, signed bounds, unequal
free masses, offset anchors, stops, mutations, sleep, suspension, friction and
contact. Eight Jolt witnesses at 60 Hz compare trajectories and efforts in
Native Debug/Release against independent mechanics. Rigid impacts, rotating
rail transients and general spatial chains remain open; no cost parity is claimed.

`SliderCombinedScene.sx` compares the combined gold carriage to a position-only
blue carriage; green markers show the moving target. T reverses and resumes,
R restarts, Space pauses/resumes, with visible buttons and status.
