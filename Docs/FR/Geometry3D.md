# Premières valeurs de géométrie 3D

`GFX.Physics` fournit des sphères, des boîtes et des poses rigides en valeurs
Silex. Ces valeurs peuvent être créées sans monde, scène ni renderer. Le monde
physique 3D et les requêtes entre formes ne sont pas encore disponibles.

```silex
use GFX.Physics
use STD.Math

let sphere = Physics.Shape3D.sphere(Physics.Sphere3D(0.5))
let box = Physics.Shape3D.box(Physics.Box3D(Math.Vec3(2.0, 1.0, 3.0)))
let pose = Physics.Transform3D(
    position:Math.Vec3(2.0, 3.0, 4.0),
    rotation:Math.Quat.angle_axis(Math.half_pi(), Math.Vec3.up())
)
let point = pose.point(Math.Vec3.right())
assert(pose.inverse_point(point).nearly_equal(Math.Vec3.right(), 0.00001))
```

`Box3D` reçoit les dimensions complètes, centrées sur l'origine locale ;
`half_size()` retourne les demi-dimensions. `Sphere3D` reçoit un rayon positif.
Les deux formes refusent les valeurs non finies ou non positives. Une
`Transform3D` conserve une position finie et un quaternion unitaire. Ses
opérations `point` et `vector` appliquent la rotation ; `point` ajoute aussi la
translation. `inverse_point` et `inverse_vector` défont ces opérations.

La convention est celle de `STD.Math` : repère droit, Y vers le haut. La pose
est sans échelle ; les dimensions appartiennent à la forme. Les transformations
ne corrigent pas silencieusement un quaternion invalide.
