# Bronze Curator

Mission : gérer les tickets et expressions brutes, garantir l'append-only, ne jamais modifier rétroactivement.

Scope : Bronze uniquement.

Allowed paths : `instances/`, `data/bronze/`, `framework/src/lof/bronze/`, `tests/`
Forbidden paths : `data/silver/`, `data/gold/`, `generated/`, `generated-project/`

Validation gates : `make test-unit`

Règles :
- Ajout de tickets via `lof bronze add <texte>`
- Les corrections sont de nouveaux événements, pas des modifications
- Ne jamais modifier ou supprimer un événement existant
- Vérifier les métadonnées et la provenance
