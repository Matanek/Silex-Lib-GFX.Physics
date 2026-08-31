# Intégration Application, ECS et Scene2D

`Plugins.Physics2D` installe un `Resources.World2D` indépendant dans le
contexte Application courant. Le plugin ajoute seulement ECS et l’horloge de
l’application : il n’impose ni fenêtre, ni renderer, ni caméra, ni panneau de
statistiques.

```silex
use GFX.Application
use GFX.Components
use GFX.ECS
use GFX.Physics
use GFX.Plugins
use GFX.Resources
use STD.Math

var application = Application()
    ..add_plugin(Plugins.Physics2D(Plugins.Physics2D.Settings()
        ..world = (Physics.World2DSettings() ..gravity = Math.Vec2(0.0, 9.81))
        ..fixed_delta = 1.0 / 60.0
        ..maximum_catch_up_steps = 4
        ..scene_units_per_meter = 100.0
        ..execution = Physics.Physics2DExecutionMode.workers(4)
    ))
```

Une entité est liée au monde lorsqu’elle possède simultanément
`Components.Transform2D` et `Components.PhysicsBody2D` :

```silex
world.spawn(ECS.EntityRecipe()
    ..with(Components.Transform2D(position:Math.Vec2(0.0, 4.0)))
    ..with(Components.PhysicsBody2D(Physics.RigidBody2DSettings()
        ..shape = Physics.Shape2D.circle(Physics.Circle2D(0.25))
        ..enable_move_events = true
    ))
)
```

`scene_units_per_meter` convertit les positions Scene2D vers le contrat en
mètres du monde physique. Le `Transform2D` ECS fixe la pose initiale. Ensuite,
le monde physique est autoritaire pour les corps dynamiques et republie leur
pose après les pas de la frame. Pour les corps fixes, le transform ECS est copié
avant chaque pas. Pour les cinématiques, il devient une cible atteinte sur le
prochain pas fixe.

Le tableau optionnel `colliders` de `PhysicsBody2D` décrit la totalité des
colliders composés du corps. Lorsqu’il n’est pas vide, le collider implicite de
`RigidBody2DSettings` est désactivé. Les réglages de création restent immuables ;
remplacer le composant recrée explicitement le corps.

## Cadence et événements

L’accumulateur conserve tout retard qui dépasse `maximum_catch_up_steps` : le
plugin le traite aux frames suivantes au lieu de supprimer des pas. Chaque pas
terminé contribue, dans l’ordre, à `Resources.Physics2DFrameEvents`. La
ressource publie le nombre de pas et les mouvements, débuts/fins/impacts de
contact ainsi que les débuts/fins/recouvrements de capteur. Elle est vidée au
début de la mise à jour physique suivante.

Le mode `synchronous` emploie un worker. `workers(count)` crée le pool persistant
du monde ; ces deux modes conservent la même séquence logique.

Les commandes ECS sont appliquées à `post_update`. Une création devient donc
physique lors de la mise à jour suivante. Une destruction ou le retrait de
l’un des deux composants invalide exactement une fois le handle correspondant
lors de cette même réconciliation. Aucun `ECS.Query` n’échappe au système qui
le reçoit.

La preuve isolée est
[`ApplicationIntegration.sx`](../../Tests/Consumer/Tests/ApplicationIntegration.sx).
