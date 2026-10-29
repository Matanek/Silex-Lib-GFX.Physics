# Simulate a 3D world with several workers

`World3D` uses one thread by default. Call `world.enable_parallelism(4)` between
steps to distribute independent physical work. The same world can return to
one worker with `world.enable_parallelism(1)`, which closes its pool.
`world.worker_count()` returns the configured count.

```sx
use GFX.Physics

func main() {
    var world = Physics.World3D()
    world.enable_parallelism(4)
    world.create_rigid_body()
    world.step(1.0 / 60.0)
    world.enable_parallelism(1)
}
```

The count must be positive. Reapplying the current count does not recreate
workers. Each world owns its pool and waits for it during destruction.
A zero step keeps its behavior and starts no work.

## Ordering and world access

`step` remains synchronous: its jobs have completed and contacts and events
have been published when it returns. Keep all world and handle access on the
calling thread between steps; the world does not provide concurrent mutation.
A mutation or reentrant step during simulation is rejected.

Body integration and contact geometry use independent ranges. The velocity
solver distributes contacts and joints while preserving calculation order for
each modified body. Point order within a contact and row order within a joint
are preserved. Contacts may share fixed supports for reading; joints retain
dependencies on both bodies.

On the same target, with identical sources, build and inputs, states and
observations retain exact equality between one and four workers in the
[qualification consumer](../../Tests/Consumer/Tests/ParallelWorld3D.sx).
This does not promise floating-point identity across different architectures.

## When to increase the worker count

Small batches run directly. Long connected chains can require sequential
stages. World preparation, waking, vehicles, position correction, CCD and
publication keep their sequential order. More workers therefore do not
guarantee a speedup; measure a representative workload without rendering
before selecting the count.

The [internal witness](../../Tests/ParallelWorkers3D.sx) checks four simultaneous
executions in all five distributed phases. It is separate from cost measurements:
its rendezvous points only serve as concurrency evidence.
