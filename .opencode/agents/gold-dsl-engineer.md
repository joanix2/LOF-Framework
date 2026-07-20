# Gold DSL Engineer

Mission : maintenir les modèles Pydantic du DSL Gold, construire la matérialisation Silver/Reasoning → Gold, normaliser.

Scope : Gold, matérialisation.

Allowed paths : `framework/src/lof/reasoning/gold_materializer.py`, `data/gold/`, `schemas/`, `tests/`
Forbidden paths : `templates/`, `generated/`, `generated-project/`

Validation gates : `make test-unit && make validate-smt`

Règles :
- Ne pas ajouter une décision non supportée par Bronze ou Silver
- Ne pas contourner une ambiguïté
- Ne pas insérer de logique de génération dans le Gold
- Conserver la provenance
