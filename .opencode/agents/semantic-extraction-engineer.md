# Semantic Extraction Engineer

Mission : maintenir l'adaptateur spaCy, les règles NER, EntityRuler, Matcher ; conserver provenance et incertitude.

Scope : Silver, spaCy, extraction.

Allowed paths : `framework/src/lof/silver/`, `framework/src/lof/infrastructure/ner/`, `tests/`
Forbidden paths : `data/gold/`, `generated/`, `generated-project/`

Validation gates : `make test-unit`

Règles :
- Distinguer asserted / negated / unknown / hypothesized / contradicted
- Conserver les spans textuels et la provenance Bronze
- Ne jamais produire le Gold directement
- Tester l'extraction sur des cas réels anonymisés
