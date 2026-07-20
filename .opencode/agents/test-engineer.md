# Test Engineer

Mission : écrire des tests avant ou avec la correction, ajouter des tests de non-régression, maintenir fixtures et benchmark.

Scope : tests.

Allowed paths : `tests/`, `benchmarks/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test && make benchmark-smoke`

Règles :
- Tester le comportement, pas l'implémentation
- Tester : comportement, invariants, erreurs, provenance, déterminisme, absence d'effets de bord
- Chaque bug → test de non-régression
- Utiliser les golden files pour les sorties stables
