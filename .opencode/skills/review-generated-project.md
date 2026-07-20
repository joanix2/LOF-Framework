# review-generated-project

Objectif : valider le projet généré (linters + tests).

## Étapes

1. Compiler le projet : `make compile`
2. Linter le backend généré : `ruff check generated-project/apps/api --ignore F821,E402,N815,F401`
3. Tester le backend généré : `cd generated-project/apps/api && pip install -e ".[dev]" && python -m pytest tests -q`
4. Vérifier l'absence de fichiers interdits
5. Vérifier le déterminisme : compiler deux fois et comparer les hashs
6. Produire un rapport : fichiers générés, tests passés, problèmes détectés
