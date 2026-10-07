# Amortir une butée de charnière

`limit_spring` permet de dépasser temporairement une borne angulaire sous la
charge, puis de revenir avec une réponse amortie. Une charnière sans ressort
conserve ses butées rigides. Cet exemple maintient un bras contre une butée
souple avec un moteur dont l’effort diffère selon le sens.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings() ..gravity = Math.Vec3())
    var pivot = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var arm = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(1.0,Math.Vec3(0.1))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0) ..allow_sleep = false)
    var hinge = world.create_hinge_constraint(pivot,arm,Physics.HingeConstraint3DSettings()
        ..minimum_angle = -0.3 ..maximum_angle = 0.3
        ..limit_spring = Physics.HingeLimitSpring3D(stiffness:1.6,damping:0.8)
        ..motor = Physics.HingeMotor3D(speed:1.0,minimum_torque:-0.1,maximum_torque:0.2))
    var step = 0;while step<360 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()-0.425)<0.003)
    assert(Math.abs(hinge.limit_torque()+0.2)<0.001)
    hinge.set_motor(Physics.HingeMotor3D(-1.0,-0.1,0.2))
    step = 0;while step<360 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()+0.3625)<0.003)
    hinge.set_limit_spring(null)
    step = 0;while step<60 { world.step(1.0/60.0);step++ }
    assert(Math.abs(hinge.angle()+0.3)<0.003)
}
```

Le moteur positif fournit 0,2 N·m à l’équilibre. Avec une raideur de 1,6 N·m/rad,
la butée se déforme de 0,125 rad : le bras se stabilise vers 0,425 rad malgré
la borne nominale de 0,3. Après inversion, son effort négatif de 0,1 N·m
produit une déformation de 0,0625 rad. Retirer le ressort rétablit la réponse
rigide aux mêmes bornes.

## Choisir la réponse

| Paramètre ou mesure | Sens |
|---|---|
| `HingeLimitSpring3D(stiffness, damping)` | Valeur immuable du ressort de butée |
| `stiffness` | Raideur strictement positive, en N·m/rad |
| `damping` | Amortissement non négatif, en N·m·s/rad |
| `limit_spring = null` | Butées rigides, valeur par défaut |
| `limit_torque()` | Couple signé des butées au dernier pas, en N·m |

Le ressort agit lorsqu’un angle atteint ou dépasse une borne, à partir de
l’état initial du pas. Un franchissement depuis l’intérieur l’active au pas
suivant ; la pose n’est pas projetée sur une butée souple. Dans un intervalle,
la borne inférieure pousse dans le sens positif et la supérieure dans le
sens négatif. Une butée n’attire pas un bras qui repart vers l’intérieur :
celui-ci tourne librement et peut atteindre l’autre borne. Deux bornes égales
créent un ressort angulaire bilatéral, qui peut osciller autour de leur angle.
L’angle reste signé dans [-π, π] ; le ressort choisit la borne la plus proche
sur le cercle, sans compter les tours. L’intervalle complet [-π, π] reste libre.

À amortissement nul, l’intégration numérique conserve un amortissement propre.
La masse, l’inertie et le décalage du pivot changent la réponse transitoire ;
les unités de raideur restent physiques. Les limites du couple moteur ne
bornent pas celui du ressort. Le [servo](HingePosition3D.md) conserve sa cible
bornée dans l’intervalle nominal ; la [friction](HingeFriction3D.md) reste
passive et cesse d’agir lorsqu’un moteur est installé.

## Modifier et mesurer

`set_limit_spring(Physics.HingeLimitSpring3D(...))` remplace le ressort ;
`set_limit_spring(null)` rétablit les butées rigides. Le changement efface les
réactions précédentes et réveille les corps liés, comme `set_limits`,
`set_anchors` et `set_frames`. `limit_spring()` renvoie l’instantané choisi.
La valeur rejette NaN, infini, raideur nulle/négative et amortissement négatif.

`limit_torque()` sépare les butées du moteur et de la friction ;
`reaction_torque()` contient leur effort total et les réactions d’alignement.
Une mutation de pose ou de masse d’un corps conserve la mesure du dernier pas
jusqu’au suivant ; la nouvelle mobilité est utilisée à cette prochaine résolution.
Un pas nul conserve les observations. Une charnière désactivée ou un corps
désactivé produit une mesure nulle après le prochain pas positif. Les règles de destruction et de validité sont celles de
la [charnière](Hinge3D.md).

La qualification couvre les deux sens, l’intérieur libre, les oscillations,
les bornes égales, deux inerties, un pivot excentré, les mutations, les moteurs,
la friction et une chaîne chargée dans son plan avec contacts réels. Les
trajectoires et efforts sont comparés à Jolt en Native Debug/Release sur
macOS ARM64. Cela ne qualifie pas les chaînes spatiales générales.

La [commande combinée](HingeCombined3D.md) suit un angle et une vitesse actualisés ensemble.
