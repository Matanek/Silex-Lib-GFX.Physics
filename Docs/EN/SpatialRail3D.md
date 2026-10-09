# Carry a slider outside the arm plane

A hinge connected to the world can hold an arm carrying a vertical slider
and an offset load. This assembly transmits forces and torques in three
dimensions; the load descends to the floor and rises after motor reversal.

The [public consumer](../../Tests/Consumer/Tests/SpatialRail3D.sx) exercises
16 recipes at 60/120 Hz, with/without a floor, payload masses 1/2 kg and
lateral offsets ±0.8 m. From the workspace root:

```sh
silex test Packages/GFX.Physics/Tests/Consumer/Tests/SpatialRail3D.sx
```

## Orient the slider

The arm has its center at `(0.5,0,0)`, mass 2 kg and isotropic inertia
0.4 kg·m². A Z-axis hinge connects it to the world with local anchor
`(-0.5,0,0)` and a zero velocity motor limited to 60 N·m. The sphere of
radius 0.15 m starts at `(1,0,±0.8)`, with isotropic inertia 0.2 kg·m².
Only the sphere can touch the floor at Y=−0.22 m; friction and restitution
are zero, gravity is Y=−9.81 m/s².

Both local slider frames rotate by π/2 around Z, taking their X axis to
vertical Y. The arm frame is at `(0.5,0,±0.8)` and the payload frame is
at its center. Initial travel is zero. Its 40 N motor drives at −0.2 m/s,
reverses to +0.2 after 2/3 s, then brakes after 4/3 s.

## Read the reactions

The slider's `reaction_force()` acts on the payload. Its opposite acts on
the arm at the moving payload point: the lever includes slider travel and
is not restricted to the rail's local anchor. `reaction_torque()` is the
additional world torque; the hinge carries the moment outside the arm plane.

The consumer checks vector translation, spin and total angular momentum
balances including the contact impulse and application point. At rest after
release, the slider supports the payload weight and the hinge supports the
assembly weight; root torque balances both weight moments. Minimum descent
is 0.07 m with the floor or 2/15 m without it.

## Scope of the proof

The public `SpatialRail` recipe in Silex-Benchmarks compares Native
Debug/Release with pinned Jolt and rejects 28 corrupted witnesses per
engine/mode. Jolt supplies the point and lever, but its normal impulse is
inferred from balance: no independent normal proof. Existing bounds remain
unchanged: linear balance 1e−5, spin 0.001, step angular momentum 0.003,
integrated 0.03, geometry 0.005, root angle 0.02 and penetration 0.003.
These proofs cover this assembly, small rotations, isotropic inertia and
one frictionless contact.
