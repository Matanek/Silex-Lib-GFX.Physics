# Intégrer World3D à Application et Scene3D

`Plugins.Physics3D` installe un `Resources.World3D` dans le contexte
Application courant. Il ajoute ECS et l'horloge, mais ni fenêtre, ni renderer,
ni `Plugins.Scene3D`. Un consommateur headless peut donc employer les mêmes
composants que la [démonstration Scene3D](../../../../Silex-Examples/Sources/Physics3D/RigidScene.sx).

```silex
use GFX.Application
use GFX.Components
use GFX.ECS
use GFX.Physics
use GFX.Plugins
use GFX.Resources
use STD.Math

var application = Application()
    ..add_plugin(Plugins.Physics3D(Plugins.Physics3D.Settings()
        ..world = (Physics.World3DSettings() ..gravity = Math.Vec3())
        ..fixed_delta = 1.0 / 60.0
        ..maximum_catch_up_steps = 4
    ))

func create_body(world:&Resources.World) {
    world.spawn(ECS.EntityRecipe()
        ..with(Components.Transform3D(position:Math.Vec3(0.0, 3.0, 0.0)))
        ..with(Components.PhysicsBody3D(Physics.RigidBody3DSettings()
            ..shape = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(0.8)))))
    )
}
```

Une entité reçoit un corps lorsqu'elle porte à la fois
`Components.Transform3D` et `Components.PhysicsBody3D`. La pose ECS est
globale et exprimée en mètres ; `Node3D` compose déjà la pose de ses parents
avant de publier son composant ECS. L'échelle globale doit être l'unité :
dimensionner la forme et le mesh explicitement. Une échelle non unitaire,
une position ou une rotation physique invalide est rejetée. Le plugin ne
convertit pas silencieusement les poses.
`Nodes.StaticBody3D` fournit un obstacle fixe sous un parent `Node3D` avec
cette même composition globale.

À la création, la pose ECS initialise le corps. Ensuite, la physique est
autoritaire pour un corps dynamique et republie sa position et sa rotation
sur `Components.Transform3D` après chaque pas. La pose ECS pilote un corps
fixe ou sert de cible au cinématique au prochain pas fixe. Une modification
externe du composant dynamique est remplacée par la pose physique ; employer
le handle `PhysicsBody3D.body()` et les commandes du corps pour le déplacer.
La liaison tient compte du cycle de vie et de la génération de l'entité.

Le plugin accumule le temps de frame et traite au plus
`maximum_catch_up_steps` pas de durée `fixed_delta` par frame. Le reliquat
attend la frame suivante. Pendant la pause `Application.Simulation`, aucun
pas n'a lieu et le temps de pause n'entre pas dans l'accumulateur. Une entité
désactivée conserve son corps mais le retire des collisions ; elle retrouve
son réglage d'activation antérieur à la réactivation. Retirer l'entité ou
l'un des deux composants détruit le corps, y compris pendant la pause.

`Resources.Physics3DFrameEvents` recueille les débuts et fins de contact de
tous les pas d'une frame, avec `fixed_step_count()`, `contact_begin_count()`,
`contact_end_count()`, `contact_begin(index)` et `contact_end(index)`. La
ressource est vidée à chaque `post_update`, même pendant une pause. Une fin
mise en attente par destruction devient visible au prochain pas positif.
Les snapshots de `Contact3D` suivent les règles du [monde 3D](World3D.md).

Un plugin consommateur peut inscrire `Physics.Physics3DStep.before_step` et
`after_step` depuis sa méthode `build`. Chaque callback `func(Application,
float)` s'exécute une fois par pas réel, après la liaison des corps et à une
frontière sûre sans query ECS active. Physics2D et Physics3D possèdent des
mondes, accumulateurs, callbacks et événements distincts dans une même
Application. La scène lit les poses physiques à `Schedule.render`, après le
`post_update` de la physique.

La preuve headless est
[`Application3DIntegration.sx`](../../Tests/Consumer/Tests/Application3DIntegration.sx).
