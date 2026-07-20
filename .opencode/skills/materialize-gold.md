# materialize-gold

Objectif : construire le Gold à partir du Silver et des inférences.

## Étapes

1. Exécuter `lof gold build`
2. Vérifier les fichiers produits dans `data/gold/instances/`
3. Vérifier la cohérence des entités, champs, opérations
4. Vérifier la provenance des décisions
5. Exécuter `lof constraints validate` pour vérifier la cohérence SMT
6. En cas d'UNSAT, identifier la contrainte violée et corriger la source
