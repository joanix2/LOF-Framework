# feature-development

1. Analyser l'impact → `orchestrator` / `trace-pipeline-impact`
2. Ajouter un test → `test-engineer` / `add-regression-test`
3. Modifier la source → agent de la couche concernée
4. Valider la couche → `make test-unit`
5. Valider la pipeline → `make validate && make validate-smt && make compile`
6. Documenter la décision → ADR dans `docs/decisions/` si nécessaire
