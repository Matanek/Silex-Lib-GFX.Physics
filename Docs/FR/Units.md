# Utiliser des pixels ou des centimètres

Le monde Physics utilise des mètres, des secondes et des kilogrammes. Si votre
application stocke des pixels ou des centimètres, convertissez ses longueurs
avant de créer les formes, les corps et les requêtes. Convertissez les résultats
dans l'autre sens pour le rendu. L'échelle de l'application ne modifie pas les
constantes physiques du monde.

À 100 unités applicatives par mètre, une position de 300 unités devient 3 m et
un rayon de 25 unités devient 0,25 m. L'exemple complet suivant vérifie ces
conversions avec l'API publique :

```silex
use GFX.Physics
use STD.Math

func main() {
    let units_per_meter = 100.0
    var world = Physics.World2D(gravity:Math.Vec2(0.0, -981.0).divide(units_per_meter))
    var body = world.create_rigid_body(Physics.RigidBody2DSettings()
        ..shape = Physics.Shape2D.circle(Physics.Circle2D(25.0 / units_per_meter))
        ..position = Math.Vec2(0.0, 300.0).divide(units_per_meter)
        ..velocity = Math.Vec2(100.0, 0.0).divide(units_per_meter)
        ..allow_sleep = false)
    world.step(1.0 / 60.0)
    let application_position = body.position().multiply(units_per_meter)
    assert(application_position.x > 0.0)
    assert(application_position.y < 300.0)
    print("application-units-ok")
}
```

La gravité vaut ici −981 unités/s², donc −9,81 m/s². La masse reste en kg et le
pas en secondes. Pour Scene2D, le paramètre `scene_units_per_meter` de
[l'intégration Application](ApplicationIntegration.md) prend en charge la
conversion des positions de scène ; les dimensions des formes restent celles
du contrat Physics.

## Convertir les grandeurs dimensionnées

Pour `u` unités applicatives par mètre, les conversions d'entrée sont :

| Grandeur exprimée dans l'application | Valeur à fournir à Physics |
| --- | --- |
| Position, longueur, rayon, translation de requête | valeur / `u` |
| Vitesse, accélération, force, impulsion linéaire | valeur / `u` |
| Couple, inertie, impulsion angulaire | valeur / (`u` × `u`) |
| Densité surfacique en kg/unité² | valeur × `u` × `u` |
| Masse en kg, durée en secondes, angle en radians, vitesse angulaire | inchangée |
| Fréquence en Hz, ratio d'amortissement, friction, restitution | inchangée |

Ces règles supposent que la masse et le temps de l'application sont déjà en
kilogrammes et secondes. Une force déjà exprimée en newtons ne se convertit
pas : le facteur ne s'applique qu'aux grandeurs exprimées dans l'unité de
longueur applicative. Les conversions de sortie sont les inverses de ce tableau.
Une fraction de rayon ou de shape cast est sans dimension et reste inchangée.

## Conserver les seuils physiques

Les seuils de sommeil, d'impact et de restitution sont des vitesses en m/s.
Ainsi 1 m/s correspond à 100 unités/s à cette échelle. Conservez les valeurs
Physics si seul le rendu change d'unité ; convertissez un seuil personnalisé
s'il provient de l'application. Les [réglages du monde](WorldSettings.md)
donnent les valeurs par défaut.

Le [témoin exécutable](../../Benchmarks/UnitsOracle2D.sx) et l'oracle Box2D
comparent les représentations 1 et 100 unités/mètre : repos, rayon, shape cast,
placement CCD, restitution et impact sous et au-dessus de 1 m/s, sommeil sous
et au-dessus de 0,05 m/s, puis plafond à 400 m/s. Les contrôles sont conservés
dans [CheckUnits.py](../../Benchmarks/Oracle2D/CheckUnits.py). Cette preuve porte
sur ces scènes et tolérances ; elle ne garantit pas toutes les échelles ou
toutes les simulations. La différence déjà documentée de vitesse immédiatement
après placement CCD n'est pas supprimée par un changement d'unité.

Changer l'unité d'affichage ne rend pas un objet physiquement minuscule plus
grand pour le solveur et n'augmente pas la précision flottante. Gardez les
coordonnées physiques proches de leur zone utile ; ne multipliez pas directement
les coordonnées du monde par 100 en laissant ses tolérances en mètres.
