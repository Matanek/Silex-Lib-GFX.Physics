# Configure a 2D world

`World2DSettings` groups the choices that determine a world’s initial
behavior. The defaults suit a simulation expressed in meters and seconds and
preserve four substeps per `step` call.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World2D(Physics.World2DSettings()
        ..gravity = Math.Vec2(0.0, -9.81)
        ..sleep_enabled = true
        ..continuous_collision_enabled = true
        ..maximum_linear_speed = 120.0
    )

    world.step(1.0 / 60.0)
    world.step(1.0 / 60.0, substeps:8)
}
```

The first step uses the default four substeps. The second explicitly increases
the temporal resolution without changing the simulated duration.

## Default values

| Setting | Default | Intent |
| --- | ---: | --- |
| `gravity` | `(0, -9.81)` | Global acceleration in meters per second squared. |
| `sleep_enabled` | `true` | Puts stable dynamic islands to sleep. |
| `continuous_collision_enabled` | `true` | Prevents fast motion from crossing obstacles. |
| `restitution_threshold` | `1.0` | Ignores bounce below this approach speed. |
| `hit_event_threshold` | `1.0` | Publishes an impact from this approach speed. |
| `contact_stiffness_hertz` | `40.0` | Controls the physical stiffness of contacts. |
| `contact_damping_ratio` | `10.0` | Dampens contact correction. |
| `maximum_correction_speed` | `3.0` | Limits the speed used to resolve penetration. |
| `maximum_linear_speed` | `400.0` | Limits the integrated linear speed of a dynamic body. |
| `warm_start_enabled` | `true` | Reuses impulses from the previous step. |

`world.settings()` returns an independent snapshot of the current settings.
Non-finite values, negative thresholds, a zero maximum linear speed, and fewer
than one substep are rejected with a focused diagnostic. All setting changes
are forbidden during `step`.

## Change the settings

Mutations use the same intentions as the creation fields:

```silex
world.set_gravity(Math.Vec2(0.0, -3.71))
world.set_sleep_enabled(false)
world.set_continuous_collision_enabled(true)
world.set_restitution_threshold(0.5)
world.set_hit_event_threshold(2.0)
world.set_contact_tuning(30.0, 8.0)
world.set_maximum_correction_speed(2.0)
world.set_maximum_linear_speed(80.0)
world.set_warm_start_enabled(false)
```

A mutation that changes the response of established contacts wakes every
dynamic body: gravity, disabling sleep, the restitution threshold, contact
tuning, maximum correction speed, and warm start. The event threshold, linear
speed limit, and continuous mode do not wake an idle body; they apply to its
next awake motion. Re-enabling sleep lets bodies settle naturally.

## Observe the logical load

`world.counters()` returns an independent `World2DCounters`: bodies, colliders,
contacts, joints, active islands, and `logical_memory_bytes`. The last value is
a deterministic estimate of the load from live values, useful when comparing
scenes. It includes neither reserved capacities, private trees, nor allocator
telemetry and therefore does not represent the process resident memory.

The consumer test
[`WorldSettings.sx`](../../Tests/Consumer/Tests/WorldSettings.sx) covers the
settings, their effects, wake policies, substeps, and counters through the
package’s public surface.
