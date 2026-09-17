# Régler un monde 2D

Voir aussi : [Utiliser des pixels ou des centimètres](Units.md).

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

## Pause et rafraîchissement

`step(0.0)` ne recalcule ni contacts ni overlaps et ne consomme pas les forces
ou couples appliqués. Les snapshots restent ceux de la dernière mise à jour.
Les événements begin/hit/move sont vidés ; les fins de contact déjà produites
par destruction sont publiées une fois. Les fins de capteur en attente restent
différées jusqu’à une mise à jour des overlaps. Le prochain pas positif applique
les forces conservées. Ce comportement suit le pas nul de Box2D 3.1.1.

Pour prendre en compte des mutations pendant une pause, demander explicitement :

```silex
body.set_position(Math.Vec2(2.0, 1.0))
world.refresh_contacts()
```

`refresh_contacts()` actualise les contacts, les capteurs et leurs événements,
sans déplacer les corps, modifier leurs vitesses, consommer leurs forces,
progresser les minuteries de sommeil ni produire d’impact de solveur. Les
filtres et le pré-solve sont évalués ; les mutations réentrantes restent interdites.
Les réactions de ce rafraîchissement sans solveur sont nulles. Les changements
de contact peuvent réveiller les corps pour le prochain pas positif.

Les anciens usages de `step(0.0)` destinés à rafraîchir les contacts doivent
appeler `refresh_contacts()`. Les [tests publics](../../Tests/Consumer/Smokes/RefreshContacts.sx)
et le [témoin différentiel](../../Benchmarks/ZeroStepOracle2D.sx) vérifient ces
intentions séparément.

Désactiver le warm start efface les impulsions provenant du pas précédent.
Les impulsions accumulées pendant le pas courant restent réutilisées entre
ses sous-pas, pour les contacts comme pour les joints.
