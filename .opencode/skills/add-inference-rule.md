# add-inference-rule

Objectif : ajouter une règle d'inférence Datalog.

## Étapes

1. Identifier les faits d'entrée (prédicats et arguments)
2. Identifier les faits inférés par la règle
3. Choisir le mode : certain, default, hypothesis
4. Ajouter la règle dans `reasoning/profiles/fastapi_react.py`
5. Vérifier la terminaison (pas de boucle récursive infinie)
6. Ajouter la provenance dans la règle
7. Écrire un test positif (cas où la règle s'applique)
8. Écrire un test négatif (cas où la règle ne s'applique pas)
9. Tester : `make test-unit`
10. Vérifier les inférences produites : `lof reason status`
