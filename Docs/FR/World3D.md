# Faire avancer des corps libres en 3D

`World3D` simule le mouvement libre de corps fixes, cinématiques et dynamiques
sans fenêtre, scène, renderer ni ECS. Il accepte les sphères et boîtes de
`Shape3D`. Cette première étape ne détecte ni ne résout les collisions : les
corps peuvent se traverser.

Le programme suivant applique une impulsion à une boîte, avance le monde et
lit sa position. L'impulsion est exprimée en masse × distance / seconde.

```silex
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D(Physics.World3DSettings()
        ..gravity = Math.Vec3())
    var body = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..shape = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0))))
    body.apply_impulse(Math.Vec3(8.0, 0.0, 0.0))
    world.step(0.25)
    assert(body.position().nearly_equal(Math.Vec3(0.25, 0.0, 0.0), 0.00001))
    world.destroy_rigid_body(body)
    assert(!body.is_valid())
}
```

## Poses, masse et commandes

Le repère suit `STD.Math` : droit, Y vers le haut. `Transform3D.position`
place l'origine de la forme ; `rotation` est un quaternion unitaire. Les
vitesses linéaire et angulaire sont exprimées dans le monde. `world_center_of_mass()`
retourne le centre de masse, qui peut différer de l'origine de la forme.
Les angles et vitesses angulaires sont en radians. `step(delta)` reçoit des
secondes et rejette une durée négative ou non finie.

Par défaut, un corps est dynamique, porte une sphère de rayon 0,5 et reçoit
une densité de 1. La masse et les trois moments d'inertie principaux sont
calculés pour la sphère ou la boîte homogène. `MassProperties3D` permet de
fixer une masse positive, un centre local et trois moments locaux positifs ;
les axes principaux coïncident alors avec les axes locaux de la forme.
L'inertie est orientée dans le monde pour les couples et impulsions. Une
impulsion ou force avec un point d'application mondial produit aussi un
moment autour du centre de masse. `apply_torque` et
`apply_angular_impulse` agissent directement sur la rotation.

Un corps fixe garde sa pose et refuse forces et impulsions. Un corps
cinématique avance avec ses vitesses configurées ; `move_kinematic(target,
duration)` calcule des vitesses pour atteindre une pose à une date donnée,
puis les annule. La cible est atteinte exactement si un pas couvre la fin de
la durée. `set_transform`, `set_linear_velocity`,
`set_angular_velocity`, `set_enabled` et `set_mass_properties` permettent les
changements directs. La masse ne peut être remplacée que sur un corps
dynamique.

La gravité par défaut vaut `(0, -9.81, 0)`. `gravity_scale` est fixé par
corps à la création ; l'amortissement linéaire et angulaire est nul par
défaut. Les forces et couples s'accumulent jusqu'au prochain pas positif,
puis sont effacés. Un pas nul ne déplace aucun corps et conserve ces
accumulations. L'intégration utilise une vitesse semi implicite et maintient
un quaternion normalisé ; les résultats dépendent de la taille du pas.

## Propriété et durée de vie

Chaque monde possède son stockage et ses corps. `RigidBody3D` est un handle
typé avec une génération : détruire un corps invalide toutes ses copies,
même si son emplacement est réutilisé. La fin du monde invalide également
les handles conservés, sans que ceux-ci maintiennent le monde vivant.
`is_valid()` permet de les vérifier ; toute autre lecture d'un handle périmé
échoue explicitement. Un monde refuse de détruire le corps d'un autre monde.
`write_bodies` remplit un tableau fourni par le consommateur avec les corps
vivants, sans promettre un ordre de création.

Le monde ne fournit pas encore de contacts, matériaux, sommeil, contraintes,
requêtes spatiales ni CCD. Les [requêtes géométriques autonomes](Geometry3D.md)
restent disponibles pour les formes isolées.
