# Joints de filtrage et contacts existants

Un `FilterJoint2D` actif interdit la collision entre ses deux corps. Créez-le
pour suspendre leurs contacts, puis détruisez-le pour réautoriser la collision :

```silex
let filter = world.create_filter_joint(first, second)
world.step(1.0 / 60.0)
// Les contacts entre first et second sont supprimés.
world.destroy_joint(filter)
world.step(1.0 / 60.0)
// Les contacts sont redécouverts si les formes sont proches et les autres filtres les autorisent.
```

La création s’applique aussi aux contacts déjà présents : ils ne produisent
plus de réponse physique au pas suivant et les événements de fin activés sont
publiés. La destruction demande une nouvelle recherche de contacts, sans
exiger de déplacer les corps. Un autre joint bloquant ou un filtre de collider
peut toujours empêcher leur retour.

Le filter joint ne possède pas de commutateur `set_collide_connected` : sa
présence exprime l’interdiction. Détruire ce joint invalide son handle. Les
joints mécaniques conservent leur réglage `set_collide_connected`, car ils
peuvent continuer à contraindre les corps tout en autorisant leur collision.

## Différence avec Box2D 3.1.1

La référence brute conserve les contacts déjà présents lors de
`b2CreateFilterJoint`. Ils peuvent continuer à freiner les corps malgré le
nouveau joint. Sa destruction ne demande pas non plus, à elle seule, la
redécouverte immédiate d’une paire immobile. Physics applique la nouvelle
politique au prochain pas dans les deux cas.

Le témoin C conserve ces résultats bruts. Son mode `--immediate` utilise
uniquement l’API publique de la référence pour exprimer le même usage :
`b2Joint_SetCollideConnected(true)` puis `false` juste après création d’un
filter joint, et `true` juste avant destruction d’un joint bloquant. Il ne
modifie pas la référence et ne prétend pas que les appels bruts sont équivalents.

Le [témoin Silex](../../Benchmarks/FilterJointOracle2D.sx) compare 24 étapes :
création avant/après contact, séparation, réentrée, destruction, mutation et
répétition du réglage d’un joint motor sans force. Les deux surfaces gardent
leurs identités dans les événements et les contacts. Position, vitesse et
impulsion vérifient aussi la conséquence physique. Le comparateur exige que
les neuf étapes divergentes du parcours brut restent explicitement identifiées.
