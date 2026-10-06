# Assembler deux corps rigidement

`World3D.create_fixed_constraint` conserve la position et l’orientation
relatives de deux corps. Sans réglages explicites, l’attache capture leur pose
courante : une poutre, sa charge et un support mobile peuvent ainsi former un
assemblage. Au moins un des deux corps doit être dynamique ; tous deux doivent
être distincts et appartenir au même monde.

Cette charge de 2 kg, décalée de 2 m, reste suspendue. Sa réattache capture
ensuite sa position après une chute :

```sx
use GFX.Physics
use STD.Math

func main() {
    var world = Physics.World3D()
    var support = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..body_type = Physics.BodyType3D.fixed ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var weight = world.create_rigid_body(Physics.RigidBody3DSettings()
        ..transform = Physics.Transform3D(Math.Vec3(2.0,0.0,0.0))
        ..mass_properties = Physics.MassProperties3D(2.0,Math.Vec3(0.2))
        ..allow_sleep = false ..collision_filter = Physics.CollisionFilter3D(mask_bits:0))
    var attachment = world.create_fixed_constraint(support,weight)
    var step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(attachment.anchor_error().length() < 0.001)
    assert(attachment.angular_error().length() < 0.001)
    assert(Math.abs(attachment.reaction_force().y-19.62) < 0.05)
    assert(Math.abs(attachment.reaction_torque().z-39.24) < 0.1)
    world.destroy_fixed_constraint(attachment)
    step = 0
    while step < 30 { world.step(1.0 / 60.0); step++ }
    assert(!attachment.is_valid() && weight.position().y < -1.0)
    let captured = weight.transform()
    attachment = world.create_fixed_constraint(support,weight)
    step = 0
    while step < 120 { world.step(1.0 / 60.0); step++ }
    assert(weight.position().nearly_equal(captured.position,0.001))
    assert(world.fixed_constraint_count() == 1)
    print("Fixed attachment: support, detach and current-pose reattachment verified")
}
```

La force de soutien vaut 19,62 N et le couple 39,24 Nm autour de Z. Détruire
l’attache libère la charge ; créer une nouvelle attache sans settings fixe la
nouvelle pose relative. La réattache ne ramène pas automatiquement la charge
à son ancienne position.

## Choisir et modifier les repères

`FixedConstraint3DSettings.first_local_frame` et `second_local_frame` sont des
`Transform3D`, identité par défaut. Avec des settings explicites, leurs origines
et orientations doivent coïncider dans le monde. Les positions sont relatives à
l’origine des corps, indépendamment du centre de masse ; les rotations sont
locales, unitaires et finies. `Transform3D` refuse une pose invalide.

`first_local_frame()` et `second_local_frame()` retournent des copies.
`set_frames(first, second)` remplace les deux repères atomiquement, efface les
réactions précédentes et réveille les corps. Une pose initialement éloignée de
la cible est corrigée progressivement pendant les pas ; l’attache ne téléporte
pas les corps à sa création.

## Mesurer l’assemblage

`anchor_error()` est le vecteur mondial du premier ancrage vers le second.
`angular_error()` est le vecteur mondial de rotation du premier repère vers
le second : sa direction est l’axe signé et sa norme l’angle le plus court en
radians, dans `[0, pi]`. À pi, l’axe peut changer de signe sans changer la pose.

`reaction_force()` et `reaction_torque()` donnent l’effort exercé sur le second
corps pendant le dernier pas, en N et Nm dans le monde ; le premier reçoit
l’opposé. Le couple est l’effort angulaire pur de l’attache : le moment de la
force d’ancrage autour du centre de masse s’ajoute à cet effort. Les réactions
sont des observations du solveur, y compris sa correction d’erreur ; elles ne
sont pas une limite de rupture. Un pas nul conserve les observations.

## Suspendre ou détruire l’attache

`set_enabled(false)` suspend l’effort sans détruire le handle ; sa réactivation
reprend la correction vers les repères existants. Chaque mutation d’attache
réveille les corps et remet ses réactions à zéro. Un corps désactivé suspend
également l’effort. Les attaches partagent les contacts et îlots de sommeil du
[monde 3D](World3D.md).

`destroy_fixed_constraint()` ou la destruction d’un corps lié invalide le
handle. `is_valid()` reste utilisable ensuite ; les autres opérations refusent
un handle périmé, y compris après réutilisation d’un slot ou destruction du
monde. `fixed_constraint_count()` compte les attaches vivantes, activées ou non.

La scène `Silex-Examples/Sources/Physics3D/FixedScene.sx` montre un support en
translation/rotation, une poutre et deux charges. `D` détache la charge bleue,
`C` la rattache à sa pose courante, `M` arrête le support, `I` donne une
impulsion, `R` réinitialise et Espace met en pause.
