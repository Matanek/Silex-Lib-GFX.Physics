# Compose a motorized shoulder and elbow

The [headless consumer](../../Tests/Consumer/Tests/ArticulatedPose3D.sx)
combines a `SwingTwistConstraint3D` shoulder with a `HingeConstraint3D`
elbow. Two offset bodies transmit their weight to a fixed support. The
shoulder’s three servos and the elbow servo change targets together,
reverse and finally recenter.

The upper body weighs 2 kg; the lower body weighs 1 or 2 kg. Their isotropic
inertias are 0.4 and 0.2 kg·m². Centers, anchors and frames are offset and
rotated. Gravity is −9.81 m/s² on Y. Capacities are 60 N·m per shoulder axis
and 40 N·m at the elbow. Stiffness/damping are 120/20 at the shoulder and
80/15 at the elbow. Each target lasts four seconds at 60 or 120 Hz.

## Effort frame during a step

A hinge carried by a moving body transports its cached effort with the
first body’s rotation. Its angular solver axes are those at the start of the
positive step and remain consistent throughout that step, including after
pose advancement. This prevents old-frame torque from contaminating the
new motor budget. Public signatures are unchanged; mutation still clears
outdated reactions.

Vector torques include axis alignment. Their motor component uses the axis
at step start; relative speed is observed in the current frame after the step.
Average anchor forces may have been applied both before and after pose
advancement. Their moment around the center cannot therefore be reconstructed
using a single initial lever.

## Evidence and scope

The pinned Jolt witness compares equilibria in Native Debug/Release with
identical targets and budgets. The comparator checks continuity, frames,
each body’s linear momentum, anchors, reversal and force/torque equilibria.
Steady admissible differences are 0.005 rad for each joint, 0.003 rad/s in
speed, 0.05 N and 0.05 N·m in reactions. Transient differences are measured.

A separate Silex diagnostic retains both force-application phases and checks
each body’s spin balance below 0.001 kg·m²/s without changing ordinary outputs.
The raw per-step world residual stays below 0.003 kg·m²/s; its raw sum measures
phase timing and pose corrections, rather than independently proving exact
conservation. The initial 0.03 cumulative bound did not apply to this chain:
the same witness rejected Jolt too. Initial traces and the counterexample
remain preserved alongside split-phase balances.

This recipe has no contacts or self-collisions. It prepares an articulated
pose but does not yet provide a ragdoll facade, imported hierarchy or general
transient parity. Destroying the upper body invalidates both joints; the
lower body’s handle remains alive.
