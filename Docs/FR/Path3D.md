# Guidage sur chemin 3D

`World3D.create_path_constraint` guide l’ancrage d’un corps sur un chemin
porté par un autre corps. La distance, les cibles et les vitesses sont en
mètres et m/s. Le chemin peut être ouvert ou bouclé et sa géométrie reste
immutable. Les deux directions normales sont contraintes ; la tangente
reste libre ou reçoit un moteur, une friction et les butées d’un chemin ouvert.

```silex
use GFX.Physics
use STD.Math
func main() {
    var world=Physics.World3D(Physics.World3DSettings() ..gravity=Math.Vec3())
    var carrier=world.create_rigid_body(Physics.RigidBody3DSettings() ..body_type=Physics.BodyType3D.fixed
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var carriage=world.create_rigid_body(Physics.RigidBody3DSettings() ..allow_sleep=false
        ..mass_properties=Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..collision_filter=Physics.CollisionFilter3D(mask_bits:0))
    var route=Physics.Path3D.line(Math.Vec3(),Math.Vec3(10.0,0.0,0.0),Math.Vec3(0.0,1.0,0.0))
    var guide=world.create_path_constraint(carrier,carriage,Physics.PathConstraint3DSettings(route)
        ..orientation=Physics.PathOrientation3D.follow_path
        ..motor=Physics.LinearMotor3D.position(3.0,20.0,40.0,12.0))
    var step=0;while step<300 { world.step(1.0/60.0);step++ }
    assert(Math.abs(guide.position()-3.0)<0.001 && guide.anchor_error().length()<0.001)
    guide.set_motor(Physics.LinearMotor3D(1.0,12.0));world.step(1.0/60.0)
    assert(guide.speed()>0.0 && guide.motor_force()<=12.001)
    guide.set_motor(null);guide.set_maximum_friction_force(6.0)
    step=0;while step<60 { world.step(1.0/60.0);step++ }
    assert(Math.abs(guide.speed())<0.001)
    world.destroy_path_constraint(guide);assert(!guide.is_valid())
    print("path recipe: ok")
}
```

## Géométrie et repères

`PathKnot3D(position, tangent, normal)` décrit un nœud Hermite. La longueur de
la tangente règle la forme du segment ; la normale est normalisée après
projection perpendiculaire à cette tangente. `Path3D(knots, closed=false)`
possède sa copie des nœuds : au moins deux pour un chemin ouvert, trois pour
une boucle. Les coefficients, longueurs et projections doivent être finis et
représentables ; chaque segment doit garder une tangente non nulle et une
normale indépendante sur tout son intervalle. Les tangentes et normales
partagées aux nœuds rendent le repère continu. Les cuspides et l’annulation
de la normale interpolée échouent explicitement. Les segments dégénérés ou
numériquement trop petits sont refusés.

`Path3D.line(start, end, normal)` construit une droite Hermite.
`length`, `is_closed`, `knot_count` et `knot` observent sa géométrie.
`frame(distance)` fournit une `Transform3D` locale au chemin : X tangente,
Y normale, Z binormale, avec X × Y = Z. La distance est projetée sur les
extrémités ouvertes ou ramenée dans la boucle ; elle doit être finie et
représentable par rapport à la longueur. Les tables de longueur d’arc sont
préparées à la création ; les requêtes inversent cette distance en paramètre
local, sans exposer un index fractionnaire de segment.

`closest_position(point, hint=0.0)` retourne la distance en mètres du point le
plus proche. La recherche examine toutes les racines stationnaires des
segments et leurs extrémités. Le hint départage les distances égales, notamment
aux intersections ; il ne force pas une branche qui serait plus éloignée.
La normale est interpolée puis réorthogonalisée au long de chaque segment.

`PathConstraint3DSettings(path)` reçoit le chemin. `first_local_path_frame`
est relatif au repère de forme du premier corps, identité par défaut ;
`second_local_anchor` est local au second corps, origine par défaut.
La position initiale et la référence d’orientation sont capturées dans
l’assemblage courant. Le chemin suit le porteur, fixe, cinématique ou dynamique.

## Commandes et orientation

`motor: LinearMotor3D?` réutilise les commandes de vitesse, position et
position/vitesse, avec bornes signées en N, raideur en N/m et amortissement en
N·s/m. Les cibles ouvertes sont projetées sur les extrémités ; les cibles
bouclées prennent le sens de l’erreur d’arc la plus courte.
`maximum_friction_force` freine passivement en N lorsque le moteur est absent.
Une commande de vitesse non nulle combinée à une cible fixe crée l’équilibre
discret cible + vitesse × (amortissement + dt × raideur) / raideur : cette
forme ne déplace pas automatiquement la cible au cours du temps.

`PathOrientation3D` propose `free`, `around_tangent`, `around_normal`,
`around_binormal`, `follow_path` et `relative_to_body`. Les modes autour d’un
axe conservent une seule rotation libre et suivent les deux autres directions.
`follow_path` conserve l’orientation capturée dans le repère du chemin ;
`relative_to_body` conserve celle du porteur. La dérivée analytique du repère
introduit la vitesse angulaire liée à la courbure et à la torsion de la normale.
Ses réactions échangent impulsion linéaire et couple, avec l’inertie effective
correspondante. Le guidage est localement linéarisé par pas : garder un pas
assez petit face aux changements de direction et de normale.

## Observations et mutations

`position()` mesure la distance courante sur le chemin ; `speed()` mesure
la vitesse relative des ancrages sur sa tangente. `anchor_error()` retourne
le vecteur du point du chemin vers l’ancrage, dans le monde ; il inclut le
dépassement longitudinal d’une extrémité. `reaction_force()` retourne la
force mondiale sur le second corps ; `reaction_torque()` retourne le couple
libre d’orientation en N·m, hors moment du levier de l’ancrage.
`motor_force()` et `friction_force()` séparent les efforts tangentiels signés.
Les réactions proviennent du dernier pas positif ; un pas nul les conserve.
La correction de pose ne change pas les vitesses.

`set_path`, `set_frames` et `set_orientation` recapturent la référence
d’orientation dans la pose courante. `set_motor`, `set_maximum_friction_force`
et `set_enabled` conservent cette référence. Toutes les mutations effacent
les réactions et réveillent les corps. Les getters correspondants permettent
l’inspection. Suspendre un corps ou la contrainte interrompt sa résolution.

Les deux corps doivent être distincts, appartenir au même monde et inclure un
corps dynamique. `path_constraint_count` compte les contraintes vivantes ;
`destroy_path_constraint` en détruit une. Détruire un corps ou le monde invalide
ses handles ; la génération empêche leur réactivation par recyclage. `is_valid`
reste utilisable après destruction, les autres opérations périmées échouent.

## Qualification et frontière de la référence

Les témoins Jolt Debug/Release couvrent droite, vitesse, position et commande
combinée sur une droite d’un mètre, friction, cinq orientations, cadre tourné
et boucle à orientation libre. Les tests indépendants vérifient le moteur sur
des droites de longueurs différentes, le transport courbe et le transport
spatial de normale, l’inertie effective, la puissance, les contacts et la sûreté.

Le Jolt épinglé utilise une fraction de segment comme erreur du moteur de
position : sur un segment de deux mètres, son ressort change d’échelle.
Son suivi courbe corrige aussi la pose sans intégrer la dérivée de repère dans
la vitesse angulaire. Ces deux écarts sont conservés comme témoins explicites ;
ils ne remplacent pas les tests physiques par une parité artificielle.
Les chaînes spatiales générales et la phase exacte des impacts restent à
qualifier séparément.
