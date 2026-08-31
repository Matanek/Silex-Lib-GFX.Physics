# Contrat de complétude Box2D 3.1.1

GFX.Physics vise une parité comportementale utile avec Box2D 3.1.1 au commit
`8c661469c9507d3ad6fbd2fea3f1aa71669c2fe3`, sans recopier ses noms C, handles,
callbacks ni stockage dans l’API Silex.

La matrice exécutable `Benchmarks/Oracle2D/CompletenessMatrix.json` classe les
422 symboles publics épinglés dans 61 capacités. Une révision différente, un
symbole absent ou dupliqué, une preuve manquante ou une exclusion injustifiée
fait échouer la validation.

Les statuts sont : `covered` pour un comportement prouvé, `partial` pour un
sous-ensemble utile, `planned` pour une capacité absente mais planifiée,
`divergent` pour une intention exprimée autrement et `excluded` pour du
plumbing sans comportement de gameplay. Chaque statut impose preuve, Spec ou
justification appropriée.

Le contrat courant compte 12 capacités couvertes, 12 partielles, 23
planifiées, 6 divergentes et 8 exclues. Ces nombres comptent des groupes de
comportements, pas un pourcentage de complétude du moteur.

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCompleteness.py \
    --box2d-source /tmp/silex-box2d-v3.1.1
```

Box2D est un oracle de benchmark sous licence MIT ; il n’est ni lié ni livré
avec le package. La matrice décrit honnêtement la frontière courante et ne
présente jamais une capacité planifiée comme disponible.
