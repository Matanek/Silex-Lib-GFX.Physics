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
que leurs copies conservées. La sortie de portée de la seule variable monde
ne constitue actuellement **pas** une preuve de cette invalidation globale :
un handle conservé peut encore accéder à son stockage. Le cycle de vie global
reste en cours de qualification ; conservez le monde pendant l’usage des objets.

Cette composition explicite est un parcours disponible et testé. Son adoption
comme adaptation de `b2Body_GetWorld`, `b2Shape_GetWorld`, `b2Chain_GetWorld` et
`b2Joint_GetWorld` reste ouverte dans la matrice de complétude.
