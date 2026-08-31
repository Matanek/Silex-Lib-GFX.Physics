# Filtrage avancé et pré-solve

Les politiques de contact sont désactivées par défaut. Un collider demande
explicitement le filtrage custom ou le pré-solve, et le monde reçoit la
fonction correspondante. Le chemin ordinaire ne construit donc aucun snapshot
de politique.

```silex
use GFX.Physics as Physics

func traversable(pair:Physics.ContactPairSnapshot2D) bool {
    return pair.first().material.application_id.value() != 7
}

var world = Physics.World2D()
world.set_custom_filter(traversable)
world.create_collider(body, Physics.Collider2DSettings()
    ..shape = shape
    ..enable_custom_filter = true
)
```

`ColliderSnapshot2D` donne le handle, le corps, la forme, le matériau, le
filtre et l’état capteur. Il ne contient ni slot dense, ni proxy spatial, ni
référence vers un manifold interne. Appeler une mutation du monde ou d’un
handle depuis la politique échoue explicitement car `step` détient le verrou.

Le pré-solve peut conserver le contact, le désactiver pour ce pas, remplacer
son manifold ou surcharger friction et restitution :

```silex
func one_way(input:Physics.ContactPreSolve2D) Physics.ContactDecision2D {
    if input.pair().second().body().velocity().y > 0.0 {
        return Physics.ContactDecision2D() ..enabled = false
    }
    return Physics.ContactDecision2D()
}

world.set_pre_solve(one_way)
collider.set_contact_policy_options(false, true)
```

Un manifold de remplacement conserve un ou deux points finis et une normale
unitaire. La friction doit rester finie et positive ou nulle ; la restitution
reste comprise entre zéro et un. Une décision ne peut pas créer une paire qui
n’existe pas.

`PhysicsMaterial2D` choisit séparément `friction_combine` et
`restitution_combine` parmi `average`, `geometric_mean`, `minimum`, `maximum`
et `multiply`. Si les deux matériaux choisissent des modes différents, le rang
stable `average`, `geometric_mean`, `minimum`, `maximum`, `multiply` tranche.
Les défauts conservent la moyenne géométrique pour la friction et le maximum
pour la restitution.

Toutes les politiques sont évaluées sur le thread qui appelle `step`, en ordre
de paire déterministe, avant les jobs du solveur. Leur code reste responsable
de la synchronisation de ses propres effets extérieurs.
