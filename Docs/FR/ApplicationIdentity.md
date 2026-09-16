# Retrouver un objet du jeu depuis la physique

Attribuez un `application_id` à un corps, un collider ou un joint pour retrouver
l'objet correspondant dans vos données applicatives. Cette clé facultative est
un `uint64` choisi par l'application. Physics la conserve sans posséder l'objet
du jeu ni exposer ses identifiants internes.

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

La même intention existe sur `Collider2DSettings` et les settings des huit
familles de joints. Chaque handle offre `application_id()` pour lire la clé et
`set_application_id(value)` pour la remplacer ou l'effacer avec `null`.
Les handles obtenus par une requête, un événement ou `write_joints` conservent
ces opérations. La vue `Joint2D` se décompose avec `match` pour accéder au handle
de sa famille.

## Choisir et conserver la clé

`null` signifie absence ; zéro est une clé valide. Physics ne génère pas les
clés et n'impose pas leur unicité. Deux colliders d'un même objet peuvent partager
une clé ; deux mondes peuvent utiliser la même numérotation. L'application décide
quand elle retire ou réutilise ses propres entrées de dictionnaire.

La clé du corps, celle de chaque collider et celle de chaque joint sont
indépendantes. Le collider implicite d'un corps commence sans clé, même si le
corps en possède une. Un `PhysicsMaterialId2D` identifie un matériau et reste
indépendant de ces clés d'objets.

Les mutations sont permises hors `step` et `refresh_contacts`. Changer une clé
ne réveille pas un corps et ne réinitialise pas les impulsions d'un joint. Un
handle détruit refuse toute lecture ou mutation, même si le moteur réutilise
son emplacement pour un nouvel objet. Celui-ci reçoit uniquement la clé de ses
propres settings, `null` par défaut.

## Lire les identifiants d'un événement conservé

Les snapshots de collider copient `application_id` et `body_application_id` au
moment de leur capture. Les événements de contact donnent accès à ces valeurs
par `event.pair().first()` et `.second()` ; les événements de capteur et les
overlaps par `.sensor()` et `.visitor()`. Un `BodyMoveEvent2D` expose la copie
avec `application_id()`.

Ces copies restent lisibles après mutation ou destruction des objets concernés.
Elles désignent l'association capturée ; elles ne consultent pas un nouvel objet
qui aurait réutilisé un emplacement. Les handles contenus dans le snapshot
peuvent alors être invalides : vérifiez `is_valid()` avant d'accéder à leur état
vivant. Les fins de capteur conservent le dernier snapshot d'overlap, alors que
les fins de contact déclenchées par destruction capturent les valeurs juste
avant celle-ci. Ne réutilisez pas vos clés applicatives tant qu'un ancien
événement doit encore être traité.

Le [consommateur complet](../../Tests/Consumer/Smokes/ApplicationIdentity.sx)
exerce ces chemins, les requêtes, les huit familles de joints, les mutations et
la recréation. [ContactPolicies](ContactPolicies.md) détaille les autres valeurs
conservées dans les snapshots.
