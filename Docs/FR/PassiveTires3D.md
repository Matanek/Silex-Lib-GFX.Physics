# Rouler et résister au glissement avec des pneus passifs

Un pneu donne une inertie et une rotation à la roue. Le contact longitudinal
entraîne cette rotation ; le contact latéral résiste à la dérive. Le monde
résout les réactions en appelant seulement `world.step`. Le
[braquage et les freins](VehicleControls3D.md) sont optionnels ; ce parcours
montre le roulement sans commande. Un [moteur et une transmission](VehiclePowertrain3D.md) peuvent entraîner les roues.

L’[exemple sans rendu](../../Examples/PassiveTires.sx) lance un châssis de
100 kg à 3 m/s sur quatre roues immobiles. Depuis la racine du workspace :

```sh
silex run Packages/GFX.Physics/Examples/PassiveTires.sx --release
```

La vitesse se stabilise près de 2,1429 m/s et chaque roue tourne près de
7,1429 rad/s. Une partie du mouvement du châssis entraîne les roues ; leur
vitesse périphérique rejoint la vitesse de roulement. Aucun moteur ne les lance.

## Choisir un pneu

Fragment de configuration, à intégrer à une liste de roues :

```sx
Physics.Wheel3DSettings(
    Math.Vec3(-0.6, 0.0, -1.0),
    tire:Physics.Tire3DSettings(inertia:0.9, angular_damping:0.2)
)
```

`tire` vaut `null` par défaut : la [suspension seule](VehicleSuspension3D.md)
conserve son comportement sans effort tangentiel ni rotation. `Tire3DSettings`
contient l’inertie de rotation en kg·m² (0,9), l’amortissement angulaire en s⁻¹
(0,2), les directions locales `forward` (+Z) et `up` (+Y), et deux courbes de
friction. Les directions doivent être unitaires, finies et non parallèles ;
le sens avant est projeté perpendiculairement au haut. L’inertie est positive
avec inverse représentable, l’amortissement positif ou nul ; tous sont finis.
Les roues restent des degrés de rotation virtuels, sans corps rigides ni masse
supplémentaires dans le monde.

## Régler l’adhérence

`TireFrictionCurve3D(points)` copie des points `Math.Vec2(glissement, coefficient)`.
Au moins un point est nécessaire ; les abscisses sont positives ou nulles,
strictement croissantes et finies, les coefficients positifs ou nuls et finis.
La courbe interpole linéairement et conserve la valeur d’extrémité hors de
l’intervalle. `coefficient(slip)` évalue un glissement fini positif ou nul.

- `longitudinal_friction` utilise le ratio absolu `abs(omega*r-v)/max(abs(v),0.001)`.
  Défaut : `(0,0)`, `(0.06,1.2)`, `(0.2,1)`.
- `lateral_friction` utilise l’angle aigu de la vitesse tangentielle avec
  l’axe avant/arrière, **en radians**, entre 0 et π/2. Défaut : `(0,0)`, `(radians(3),1.2)`, `(radians(20),1)`.

Le coefficient effectif est la moyenne géométrique du coefficient du pneu et
de la friction du **support**. La friction du collider de châssis ne règle pas
celle du pneu. Chaque effort tangentiel est borné séparément par ce coefficient
fois l’effort normal ; ce modèle n’impose pas un cercle d’adhérence combiné.
Un sol de friction nulle ne transmet aucun effort tangentiel.

## Lire la rotation et les efforts

Le snapshot `vehicle.wheel(i)` ajoute aux observations de suspension :

- `rotation_angle`, angle signé en radians, ramené dans l’intervalle ouvert entre −2π et 2π ;
- `angular_velocity`, vitesse signée en rad/s ; positive pour rouler vers `forward` ;
- `longitudinal_slip` et `lateral_slip`, ratio et radians ;
- `longitudinal_direction` et `lateral_direction`, axes mondiaux de contact ;
- `longitudinal_force` et `lateral_force`, efforts signés en N sur le châssis.

Les axes et glissements sont évalués au début du pas, avant résolution.
La rotation avance une fois après amortissement de la vitesse initiale du pas ;
la vitesse finale et les efforts sont lus après résolution. Les efforts sont
les impulsions totales du pas divisées par sa durée. Le support reçoit la
réaction opposée au même point. En vol, angles et vitesses continuent d’avancer,
mais glissements, axes et efforts de contact sont nuls. Un pas nul conserve
l’observation ; un châssis désactivé ou endormi conserve sa rotation.

`vehicle.set_wheel_angular_velocity(i, value)` initialise explicitement une
vitesse de roue finie et représentable, puis réveille le châssis. La roue doit
avoir un pneu et le véhicule doit être vivant. Cette mutation n’est pas un
contrôleur de propulsion. Une roue tournant au-dessus de 10°/s retarde le
sommeil du châssis. Retirer le support efface immédiatement ses efforts ;
retirer le châssis invalide toutes les commandes de ses roues.

## Vérifier le comportement

Le [consommateur public](../../Tests/Consumer/Tests/VehicleTires3D.sx) contrôle
roulement, dérive, sol lisse, repères tournés, supports mobiles, bilans, sommeil
et durée de vie. Les bilans des deux corps et de la rotation des roues sont
séparés : aucune conservation du moment angulaire incluant les rotors virtuels
n’est annoncée. Les courbes à pente forte peuvent faire varier les valeurs
instantanées de glissement près du roulement sans glissement.

La campagne de qualification utilise le véritable contrôleur de roues Jolt,
couple moteur nul et transmission au neutre : roulement aligné/tourné, dérive,
déplacement diagonal, rotation libre amortie et saut en mouvement. À 60/120 Hz
en Debug/Release sur macOS ARM64, chaque moteur fournit 3072 observations et
52 gardes de corruption. Les trajectoires et rotations sont comparées à chaque
pas, avec bilans indépendants des impulsions. Les glissements sont recalculés
dans chaque moteur et comparés par moyennes de phase ; leur égalité instantanée
près de zéro n’est pas revendiquée. Les deux mondes utilisent 12 itérations de
vitesse et 4 de position, un worker et un pas sans sous-division ; Silex conserve
ses passes avant et après intégration. Cette preuve ne qualifie pas encore la
conduite, la vitesse d’exécution ni toutes les situations de terrain.
