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

La matrice courante compte 49 capacités couvertes, 7 adaptations explicites et
5 exclusions. Elle ne contient plus de capacité partielle ou planifiée. Les
réponses transitoires des joints motor/mouse et l’invalidation des handles à
la fin de vie du monde sont désormais qualifiées par leurs témoins dédiés.
Le réglage commun des cinq familles qui l’utilisent est comparé à la référence.

Les adaptations comprennent les unités fixes en mètres, les valeurs géométriques
validées, la représentation des proxies, la fin de vie du monde, le filtrage et
les mesures des joints, ainsi que la [composition explicite du monde](WorldOwnership.md).
Leurs différences avec les appels C bruts sont conservées dans la matrice et
exercées par les tests consommateurs.

La porte `--final` contrôle cet inventaire et la présence de ses preuves. Elle
ne remplace ni l’exécution des témoins physiques, ni les comparaisons de
parallélisme, ni les [budgets temporels et mémoire](OracleAndBudgets.md).
Ces budgets restent à qualifier ; l’inventaire complet ne prouve pas une parité
globale de performance ou une équivalence dans toute scène possible.

```text
python3 Packages/GFX.Physics/Benchmarks/Oracle2D/CheckCompleteness.py \
    --box2d-source /tmp/silex-box2d-v3.1.1 \
    --final
```

Box2D est un oracle de benchmark sous licence MIT ; il n’est ni lié ni livré
avec le package. La matrice décrit honnêtement la frontière courante et ne
présente jamais une capacité planifiée comme disponible.
