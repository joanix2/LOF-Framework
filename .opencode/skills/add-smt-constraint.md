# add-smt-constraint

Objectif : ajouter une contrainte SMT déclarative.

## Étapes

1. Définir l'invariant métier
2. Déterminer si SMT est nécessaire (règle statique non exprimable en JSON Schema)
3. Créer la définition déclarative dans `validation/smt/validation_engine.py`
4. Créer ou réutiliser un compilateur dans `validation/smt/compilers/`
5. Nommer les assertions pour l'unsat core
6. Définir le diagnostic (code, message, hint)
7. Créer un cas SAT
8. Créer un cas UNSAT
9. Vérifier l'unsat core
10. Vérifier qu'aucun artefact n'est généré en cas d'échec
11. Tester : `make validate-smt && make test-unit`
