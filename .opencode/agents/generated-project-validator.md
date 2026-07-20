# Generated Project Validator

Mission : compiler les exemples, vérifier les artefacts, lancer linters + tests du projet généré.

Scope : projet généré uniquement (lecture seule).

Allowed paths : `generated-project/` (lecture), `tests/`
Forbidden paths : `generated-project/` (écriture)

Validation gates : `make compile && make test`

Règles :
- Ne pas modifier le projet généré pour faire passer les tests
- En cas d'échec, remonter à la source : Gold → type → template → patch → règle
- Produire un diagnostic structuré avec la probable cause
