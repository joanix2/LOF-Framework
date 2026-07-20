# inspect-repository

Objectif : comprendre l'état du dépôt avant modification.

## Étapes

1. Lire `AGENTS.md` et `CLAUDE.md`
2. Examiner l'état Git (`git status`, `git log --oneline -5`)
3. Examiner l'arborescence (`ls -la`, `find . -name "*.py" | head -20`)
4. Identifier les fichiers impactés par la demande
5. Rechercher les implémentations similaires existantes
6. Rechercher les tests existants (`grep -r "test_" tests/`)
7. Identifier les fichiers générés exclus du scope
8. Produire une synthèse : scope, couches impactées, abstractions, tests, risques
