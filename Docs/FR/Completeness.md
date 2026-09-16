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

La matrice courante compte 47 capacités couvertes, 5 divergentes, 8 exclues
et une partielle : le réglage de souplesse des contraintes de joints. Le joint
de distance rigide possède une preuve transitoire ; les autres familles et
les combinaisons ressort/limites restent à qualifier. La porte finale doit
rester rouge tant que cette capacité est partielle. Ces nombres décrivent
l’inventaire, pas une preuve globale d’équivalence physique.

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCompleteness.py \
    --box2d-source /tmp/silex-box2d-v3.1.1 \
    --final
```

Box2D est un oracle de benchmark sous licence MIT ; il n’est ni lié ni livré
avec le package. La matrice décrit honnêtement la frontière courante et ne
présente jamais une capacité planifiée comme disponible.
