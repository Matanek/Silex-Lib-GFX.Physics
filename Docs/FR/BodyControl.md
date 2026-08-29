# Masse, forces et contrôle des corps

`RigidBody2D` rassemble les intentions qui pilotent un corps sans reproduire
l’intégration physique dans l’application. Toutes ses mutations exigent un
monde déverrouillé, donc un appel pendant `World2D.step` échoue explicitement.

## Masse composée

La masse, le centre de masse local et l’inertie de rotation dérivent de tous
les colliders vivants, de leur géométrie et de leur densité. Ajouter, supprimer
ou modifier un collider recalcule ces propriétés. Le centre monde tient compte
du transform courant du corps.

```silex
let properties = body.mass_properties()
print(properties.mass)
print(body.local_center_of_mass())
print(body.world_center_of_mass())
print(body.rotational_inertia())
```

Une surcharge explicite reste possible. Elle demeure active lors des mutations
de colliders jusqu’à son retrait :

```silex
body.set_mass_properties(Physics.MassProperties2D(
    mass:12.0,
    rotational_inertia:8.0,
    local_center:Math.Vec2(0.25, 0.0)
))

body.reset_mass_from_colliders()
```

À la création, `RigidBody2DSettings.mass = 0.0` signifie « dériver depuis les
colliders ». Une valeur strictement positive conserve le raccourci historique
de surcharge scalaire. Un corps dynamique sans masse positive ne peut recevoir
ni force ni impulsion.

## Forces et impulsions

Une force ou un couple s’accumule jusqu’au prochain `step`, puis est vidé. Une
impulsion modifie immédiatement la vitesse. Les variantes au point utilisent
un point monde et produisent aussi un effet angulaire autour du centre de
masse.

```silex
body.apply_force_to_center(Math.Vec2(20.0, 0.0))
body.apply_force(Math.Vec2(0.0, 5.0), world_point)
body.apply_torque(2.0)

body.apply_linear_impulse_to_center(Math.Vec2(1.0, 0.0))
body.apply_linear_impulse(Math.Vec2(0.0, 1.0), world_point)
body.apply_angular_impulse(0.5)
```

Chaque action accepte `wake:bool = true`. Avec `wake = false`, une action sur
un corps endormi est ignorée. Les actions physiques exigent un corps dynamique,
activé, valide et de masse positive ; couple et impulsion angulaire exigent en
plus une rotation libre.

## Repères et vitesse d’un point

Le corps convertit directement points et vecteurs entre ses repères. Les
points incluent la translation, contrairement aux vecteurs :

```silex
let world_point = body.world_point(local_point)
let local_point_again = body.local_point(world_point)
let world_direction = body.world_vector(local_direction)
let local_direction_again = body.local_vector(world_direction)

let velocity_here = body.world_point_velocity(world_point)
let velocity_there = body.local_point_velocity(local_point)
```

La vitesse linéaire publique est celle du centre de masse. La vitesse d’un
point ajoute la contribution de la vitesse angulaire.

## Contrôle d’exécution

Les réglages suivants existent à la création et restent mutables hors d’un
pas : type, échelle de gravité, amortissements, seuil et autorisation de
sommeil, rotation fixe, bullet, activation et libellé de debug. Les getters
correspondants permettent d’observer l’état courant.

```silex
body.set_body_type(Physics.BodyType2D.dynamic)
body.set_gravity_scale(0.5)
body.set_linear_damping(0.2)
body.set_angular_damping(0.4)
body.set_sleep_threshold(0.03)
body.set_sleep_enabled(false)
body.set_fixed_rotation(true)
body.set_bullet(true)
body.set_debug_label("player")
```

`set_fixed_rotation(true)` annule la vitesse angulaire et retire l’inertie de
la réponse. `set_enabled(false)` conserve le handle et son transform, mais
retire le corps des contacts, événements, requêtes et îlots au prochain pas ;
la réactivation reconstruit sa participation.

Un corps cinématique activé peut viser un transform sur une durée donnée :

```silex
body.set_target_transform(
    Physics.Transform2D(position:target_position, rotation:target_rotation),
    0.5
)
```

Cette opération choisit les vitesses linéaire et angulaire qui atteignent la
cible, en prenant le chemin de rotation le plus court. L’application continue
d’appeler `step` pendant la durée indiquée.

Les preuves consommateur sont dans
[`Tests/Consumer/Tests/BodyControl.sx`](../../Tests/Consumer/Tests/BodyControl.sx)
et les cas d’échec dans
[`Tests/Consumer/check-body-control.sh`](../../Tests/Consumer/check-body-control.sh).
Le témoin différentiel Box2D est documenté dans
[`Benchmarks/Oracle2D/README.md`](../../Benchmarks/Oracle2D/README.md).
