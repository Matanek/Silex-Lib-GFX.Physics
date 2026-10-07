# Glissière 3D

Une `SliderConstraint3D` guide un corps sur le rail du premier corps. Les axes
X des deux repères locaux définissent le déplacement libre ; leurs axes Y/Z
et leur orientation relative restent alignés. Le rail peut appartenir à un
corps fixe, cinématique ou dynamique. Au moins un des deux corps est dynamique.

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var rail = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed)
    var carriage = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..mass_properties = Physics.MassProperties3D(2.0, Math.Vec3(0.2))
        ..collision_filter = Physics.CollisionFilter3D(mask_bits:0)
        ..allow_sleep = false)
    var joint = world.create_slider_constraint(rail, carriage,
        Physics.SliderConstraint3DSettings()
        ..minimum_position = -0.5 ..maximum_position = 0.75)
    carriage.set_linear_velocity(Math.Vec3(0.5, 0.0, 0.0))
    var step = 0
    while step < 60 { world.step(1.0 / 60.0); step++ }
    assert(Math.abs(joint.position() - 0.5) < 0.0001)
    assert(joint.anchor_error().length() < 0.0001)
    assert(joint.angular_error().length() < 0.0001)
    assert(Math.abs(joint.reaction_force().y - 19.62) < 0.0001)
}
```

Les repères `first_local_frame` et `second_local_frame` sont exprimés dans
les transformations publiques des corps, avant décalage de leur centre de
masse. Par défaut ils valent `Transform3D()` ; ces repères demandent une
orientation identique et autorisent l’écartement sur X. Pour orienter le
rail, tourner les repères locaux ou le corps qui le porte. Une rotation du
premier corps transporte le rail et la vitesse du chariot.

`position()` donne en mètres la projection de l’écartement des repères sur
le X du premier repère. `speed()` est sa dérivée signée en m/s, tenant compte
du déplacement et de la rotation du rail. `anchor_error()` donne seulement
l’erreur transversale mondiale : une course libre n’est pas une erreur.
`angular_error()` est le vecteur de rotation mondial qui sépare les repères,
en radians, avec le chemin court.

`minimum_position` et `maximum_position` sont des bornes signées facultatives.
`null` ouvre le côté correspondant ; deux bornes doivent être finies et
ordonnées. Elles peuvent être égales, même hors de zéro : le dernier degré
de liberté est alors bloqué. La référence Jolt refuse ces limites rigides égales
pour sa glissière ; ce cas Silex est comparé à l’attache fixe Jolt équivalente. Les butées sont rigides et unilatérales ; elles
retiennent une vitesse sortante et permettent de repartir vers l’intérieur.

`reaction_force()` et `reaction_torque()` donnent la force mondiale en N et
le couple de réaction mondial en N·m appliqués au second corps pendant le
dernier pas positif. Le couple est le couple libre de retenue d’orientation ;
le moment de la force à l’ancrage s’y ajoute pour l’effort total au centre de
masse. `limit_force()` isole la force axiale signée des butées, positive sur
la borne inférieure et négative sur la borne supérieure. À bornes égales elle
peut prendre les deux signes. `step(0.0)` conserve les dernières mesures.

`set_frames(first, second)`, `set_limits(minimum, maximum)` et
`set_enabled(enabled)` modifient la contrainte, effacent ses réactions et
réveillent les deux corps. Les lectures de repères sont des valeurs ; modifier
les réglages utilisés à la création ne modifie pas la glissière. Désactiver
un corps suspend la contrainte et ses mesures au pas positif suivant. Les
changements de masse et de pose sont pris en compte à ce pas.

`World3D.slider_constraint_count()` compte les glissières vivantes.
`destroy_slider_constraint(joint)` invalide toutes ses références ; détruire
un corps lié ou libérer le monde les invalide également. `is_valid()` reste
consultable, les autres appels sur une référence périmée sont refusés.
Les contraintes participent aux contacts réels et aux îlots de sommeil.

Cette première tranche propose course libre et butées rigides. Moteurs,
friction axiale et butées souples restent à qualifier. Les témoins Jolt
couvrent la translation, les réactions aux butées sous charge, les repères
excentrés et les rails tournants ; la parité des transitoires d’impact et des
chaînes spatiales générales n’est pas établie. La scène `SliderScene.sx`
montre le rail incliné, la gravité et une impulsion de relance avec T ; R
réinitialise, Espace met en pause/reprend et Échap ferme.
