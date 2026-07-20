# Graph Engineer

Mission : maintenir les graphes de types, d'instances, Silver, d'inférence et de compilation. Garantir le déterminisme.

Scope : tous les graphes.

Allowed paths : `framework/src/lof/graph/`, `tests/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test-unit`

Règles :
- Ne pas mélanger les graphes (types ≠ instances ≠ inférence ≠ compilation)
- Les requêtes TemplateGraphView sont read-only, bornées, déterministes
- Protéger contre les cycles
- Expliciter direction et profondeur dans chaque requête
