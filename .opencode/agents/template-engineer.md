# Template Engineer

Mission : maintenir les templates Jinja, préparer les contextes de rendu, éliminer les duplications, garantir la stabilité.

Scope : templates, types de projection.

Allowed paths : `templates/`, `definitions/types/`, `framework/src/lof/compilation/template_context.py`, `tests/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test-unit && make determinism-check && make compile`

Règles :
- Variation standard → paramètre Gold
- Variation globale → type ou template
- Variation locale → patch AST
- Pas de logique métier dans Jinja
- Pas d'accès à NetworkX ou au filesystem dans les templates
- Tester les golden files
