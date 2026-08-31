# Mouvement cinématique de personnage

`CharacterMover2D` calcule le déplacement sûr d'une capsule sans créer de
corps dynamique pour le personnage. Le monde reste en lecture seule pendant
le calcul : le jeu applique ensuite `applied_translation` à son transform ECS
ou à son propre état de personnage.

```silex
use GFX.Physics
use STD.Math

var mover = Physics.CharacterMover2D(
    Physics.CharacterMover2DSettings()
        ..capsule = Physics.Capsule2D(
            Math.Vec2(0.0, -0.45),
            Math.Vec2(0.0, 0.45),
            0.3
        )
)

let result = mover.calculate_move(
    world,
    character_position,
    desired_velocity.multiply(delta_seconds)
)
character_position = character_position.add(result.applied_translation)
```

Le résultat indique aussi la translation restante, les colliders touchés, les
plans de collision, le nombre d'itérations et la présence d'un recouvrement
initial. Les capteurs sont ignorés par défaut. `query_filter` restreint les
catégories considérées ; `include_sensors` permet explicitement de traiter les
capteurs comme des obstacles.

## Contrôle séparé des plans

`collect_planes` collecte les plans autour de la capsule courante,
`solve_planes` dépénètre et contraint une translation, puis `clip_vector`
retire la composante qui rentre dans les plans actifs. Cette séparation permet
à un contrôleur de personnage de décider lui-même ce qui constitue le sol, un
mur praticable ou une pente trop raide.

Le nombre d'itérations est borné par `maximum_iterations` et
`maximum_plane_iterations`. `tolerance` doit être finie et strictement
positive. Les chaînes unilatérales conservent leur convention de winding.

## Exemple visuel

```text
silex run Silex-Examples/Sources/CharacterMover2D.sx --release
```

La démo montre une capsule sur un sol, une pente, une marche, un angle concave,
un trampoline, une caisse dynamique à pousser et une plateforme cinématique
mobile. Des parois retiennent les objets physiques dans l'arène. Elle appartient
au catalogue public `Silex-Examples`. Utiliser `A`/`D` ou les flèches pour se
déplacer, `Espace` pour sauter et `R` pour recommencer.
