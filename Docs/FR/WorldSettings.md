# Régler un monde 2D

`World2DSettings` regroupe les choix qui déterminent le comportement initial
d’un monde. Les valeurs par défaut conviennent à une simulation exprimée en
mètres et secondes et conservent quatre sous-pas par appel à `step`.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World2D(Physics.World2DSettings()
        ..gravity = Math.Vec2(0.0, -9.81)
        ..sleep_enabled = true
        ..continuous_collision_enabled = true
        ..maximum_linear_speed = 120.0
    )

    world.step(1.0 / 60.0)
    world.step(1.0 / 60.0, substeps:8)
}
```

Le premier pas utilise les quatre sous-pas par défaut. Le second augmente
explicitement la résolution temporelle sans changer la durée simulée.

## Valeurs par défaut

| Réglage | Défaut | Intention |
| --- | ---: | --- |
| `gravity` | `(0, -9.81)` | Accélération globale en mètres par seconde carrée. |
| `sleep_enabled` | `true` | Endort les îlots dynamiques stables. |
| `continuous_collision_enabled` | `true` | Protège les mouvements rapides contre la traversée des obstacles. |
| `restitution_threshold` | `1.0` | Ignore le rebond sous cette vitesse d’approche. |
| `hit_event_threshold` | `1.0` | Publie un impact à partir de cette vitesse d’approche. |
| `contact_stiffness_hertz` | `40.0` | Règle la raideur physique des contacts. |
| `contact_damping_ratio` | `10.0` | Amortit la correction des contacts. |
| `maximum_correction_speed` | `3.0` | Limite la vitesse utilisée pour résorber une pénétration. |
| `maximum_linear_speed` | `400.0` | Limite la vitesse linéaire intégrée d’un corps dynamique. |
| `warm_start_enabled` | `true` | Réutilise les impulsions du pas précédent. |

`world.settings()` retourne un snapshot autonome des réglages courants. Les
valeurs non finies, les seuils négatifs, une vitesse linéaire maximale nulle et
un nombre de sous-pas inférieur à un sont refusés avec un diagnostic ciblé.
Tous les changements de réglage sont interdits pendant `step`.

## Modifier les réglages

Les mutations portent les mêmes intentions que les champs de création :

```silex
world.set_gravity(Math.Vec2(0.0, -3.71))
world.set_sleep_enabled(false)
world.set_continuous_collision_enabled(true)
world.set_restitution_threshold(0.5)
world.set_hit_event_threshold(2.0)
world.set_contact_tuning(30.0, 8.0)
world.set_maximum_correction_speed(2.0)
world.set_maximum_linear_speed(80.0)
world.set_warm_start_enabled(false)
```

Une mutation qui change la réponse de contacts déjà établis réveille tous les
corps dynamiques : gravité, sommeil désactivé, seuil de restitution, réglage
des contacts, vitesse maximale de correction et warm start. Le seuil d’événement,
la limite de vitesse linéaire et le mode continu ne réveillent pas un corps
immobile ; ils s’appliquent à son prochain mouvement éveillé. Réactiver le
sommeil laisse les corps se stabiliser naturellement.

## Observer la charge logique

`world.counters()` retourne un `World2DCounters` autonome : corps, colliders,
contacts, joints, îlots actifs et `logical_memory_bytes`. Ce dernier est une
estimation déterministe de la charge des valeurs vivantes, utile pour comparer
des scènes. Il n’inclut ni capacités réservées, ni arbre privé, ni télémétrie de
l’allocateur et ne représente donc pas la mémoire résidente du processus.

Le test consommateur
[`WorldSettings.sx`](../../Tests/Consumer/Tests/WorldSettings.sx) couvre les
réglages, leurs effets, les réveils, les sous-pas et les compteurs à travers la
surface publique du package.
