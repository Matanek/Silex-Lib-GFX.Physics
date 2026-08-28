# Migrer de GFX.Physics 0.4 vers 0.5

La version 0.5 remplace l’ancien moteur par la reconstruction Silex native
fondée sur le modèle algorithmique Box2D 3. `Physics.World2D` reste l’unique
monde public : aucun sélecteur de backend ni moteur de compatibilité n’est à
configurer.

## Source existante

La surface d’intention 0.4 reste valide : monde, gravité, `step`, profiling,
workers, compteurs, buffers de transforms, réglages des corps, accès aux
transforms et vitesses, état de veille et alias des catalogues GFX. Une
application ordinaire ne migre pas son code pour choisir le nouveau cœur.

Les anciens réglages de forme, friction, restitution, filtre, capteur et
événements créent désormais un `Collider2D` implicite équivalent. Pour un corps
composé, utilisez `create_implicit_collider = false`, puis
`World2D.create_collider`.

## Changements intentionnels

- Tous les nombres de workers utilisent la même découverte de paires, le même
  cache, les mêmes îlots et le même solver Soft Step à quatre sous-pas.
- Les trajectoires flottantes exactes de l’ancien solver ne sont pas un contrat ;
  testez des enveloppes physiques et des résultats de gameplay.
- Les handles sont générationnels et leur destruction invalide les copies.
- Toute mutation du monde, des corps et des joints est refusée pendant `step`.
- Géométrie convexe, contacts persistants, joints, bullets, capteurs et
  événements post-step sont ajoutés au contrat public.

Les coûts restent opt-in : pas de CCD bullet sans bullet, pas de payload
d’événement si le flux est désactivé, et aucun solver alternatif en parallèle.

Le package est pur Silex et ne possède aucune frontière de plateforme. La
publication reste conditionnée par la matrice de portabilité, les sentinelles
graphiques et le corpus de benchmarks.
