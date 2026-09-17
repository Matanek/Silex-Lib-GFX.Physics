# Conserver le monde pour les opérations globales

Un handle permet d’agir sur son objet : position ou impulsion d’un corps,
matériau d’un collider, cible d’un joint. Pour créer un autre objet, effectuer
une requête spatiale ou détruire un objet, conservez le `World2D` concerné dans
votre scène ou passez-le explicitement à la fonction.

```silex
func spawn_neighbor(world:Physics.World2D, body:Physics.RigidBody2D) Physics.RigidBody2D {
    return world.create_rigid_body(Physics.RigidBody2DSettings()
        ..position = body.position().add(Math.Vec2(2.0, 0.0)))
}
```

Cette règle est la même pour les corps, les colliders ordinaires ou de chaîne
et les huit familles de joints. `collider.body()` et les accesseurs de corps
des joints retrouvent les corps associés ; ils ne retrouvent pas le monde.
Aucun handle ne propose actuellement `world()`.

`World2D` est une classe partagée : la conserver dans un objet de scène garde
la même simulation accessible, sans copier son état. Les
[tests consommateurs](../../Tests/Consumer/Tests/WorldOwnership.sx) exercent
création, requête, remplacement de colliders, remplacement d’un corps depuis
chacune des huit familles de joints et invalidation des handles détruits.

La destruction explicite d’un corps invalide ses colliders et joints ainsi
que leurs copies conservées. Quand la dernière référence atteignable au monde
disparaît, la simulation se termine et tous ses handles deviennent invalides :
corps, colliders, chaînes et huit familles de joints. `is_valid()` retourne
alors `false` ; lire ou modifier l’objet par ce handle échoue avec un diagnostic.
Conserver un handle seul ne prolonge pas la simulation. Conserver un alias du
monde, notamment dans une scène, la prolonge.

Un callback lié à la scène peut former un cycle avec le monde. Quand ce cycle
n’est plus atteignable, Silex le finalise également. Si un callback retire la
dernière référence extérieure pendant `step` ou `refresh_contacts`, le monde
reste vivant jusqu’au retour de l’appel actif. Les restrictions de mutation
pendant le pas continuent de s’appliquer.

Les données des snapshots de contacts et d’événements restent lisibles après
la fin du monde ; leurs handles incorporés deviennent invalides. Créer un
nouveau monde ne réactive jamais un ancien handle. Le témoin Box2D 3.1.1
épinglé montre une différence sur ce dernier point : ses IDs bruts peuvent
redevenir valides après réutilisation d’un emplacement de monde. Silex conserve
l’identité du monde d’origine et refuse cet accès à une nouvelle simulation.

Les [tests de fin de vie](../../Tests/Consumer/Tests/WorldLifetime.sx) vérifient
les aliases, les cycles, les callbacks actifs, les snapshots et l’indépendance
de deux mondes. Les [accès périmés](../../Tests/Consumer/check-world-lifetime.py)
sont vérifiés pour chaque famille de handle.

Cette composition explicite est l’adaptation retenue pour `b2Body_GetWorld`,
`b2Shape_GetWorld`, `b2Chain_GetWorld` et `b2Joint_GetWorld`.
