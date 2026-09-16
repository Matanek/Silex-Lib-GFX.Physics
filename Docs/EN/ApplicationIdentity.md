# Find a game object from physics

Assign an `application_id` to a body, collider, or joint to find the corresponding
object in your application data. This optional key is a `uint64` chosen by the
application. Physics keeps it without owning the game object or exposing its
internal identifiers.

```silex
use GFX.Physics
use STD.Collections

func main() {
    let player_id:uint64 = 42
    var names = Collections.Dictionary<uint64, str>()
    names.set(player_id, "player")
    var world = Physics.World2D()
    var body = world.create_rigid_body(Physics.RigidBody2DSettings()
        ..application_id = player_id)
    if let id = body.application_id() {
        assert(names.get(id) == "player")
    } else { panic("missing application identity") }
    body.set_application_id(null)
    assert(body.application_id() == null)
    print("application-identity-guide-ok")
}
```

The same intent is available on `Collider2DSettings` and all eight joint
settings types. Each handle offers `application_id()` to read the key and
`set_application_id(value)` to replace it or clear it with `null`. Handles
obtained through queries, events, or `write_joints` retain these operations.
Use `match` on the `Joint2D` view to access its family's handle.

## Choose and retain the key

`null` means absent; zero is a valid key. Physics does not generate keys or enforce
uniqueness. Two colliders belonging to one game object may share a key; two worlds
may use the same numbering. The application decides when to remove or reuse its
own dictionary entries.

Body, collider, and joint keys are independent. A body's implicit collider starts
without a key, even if the body has one. A `PhysicsMaterialId2D` identifies a
material and remains separate from these object keys.

Mutations are allowed outside `step` and `refresh_contacts`. Changing a key does
not wake a body or reset joint impulses. A destroyed handle rejects every read
or mutation, even if the engine reuses its storage for a new object. That object
receives only the key from its own settings, `null` by default.

## Read identifiers from a saved event

Collider snapshots copy `application_id` and `body_application_id` when captured.
Contact events expose these values through `event.pair().first()` and `.second()`;
sensor events and overlaps through `.sensor()` and `.visitor()`. A
`BodyMoveEvent2D` exposes its copy through `application_id()`.

These copies remain readable after the relevant objects are changed or destroyed.
They describe the captured association; they do not query a new object that has
reused a storage location. Handles inside the snapshot may now be invalid: check
`is_valid()` before accessing their live state. Sensor ends retain the last
overlap snapshot, whereas contact ends triggered by destruction capture values
immediately before destruction. Do not reuse your application keys while an old
event still needs to be processed.

The [complete consumer](../../Tests/Consumer/Smokes/ApplicationIdentity.sx)
exercises these paths, queries, all eight joint families, mutations, and
recreation. [Contact policies](ContactPolicies.md) describes other values
retained by snapshots.
