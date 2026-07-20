# Format des diagnostics

## Structure

```json
{
  "code": "DUPLICATE_API_ROUTE",
  "stage": "semantic-validation",
  "severity": "error",
  "message": "Deux entités utilisent la même route.",
  "sources": [
    {"file": "instances/customer.json", "path": "$.values.route"}
  ],
  "relatedIds": ["customer", "project"],
  "hint": "Attribuer des routes distinctes.",
  "repairScope": "gold"
}
```

## Champs

| Champ | Description |
|-------|-------------|
| `code` | Code stable et documenté |
| `stage` | Étape de la pipeline (bronze, silver, reasoning, gold, smt, compilation) |
| `severity` | error, warning, info |
| `message` | Explication lisible |
| `sources` | Fichiers et chemins JSON concernés |
| `relatedIds` | Identifiants d'instances ou de types |
| `hint` | Suggestion de correction |
| `repairScope` | Couche où appliquer la correction |

## Codes principaux

| Code | Signification |
|------|---------------|
| DUPLICATE_API_ROUTE | Route API dupliquée |
| DUPLICATE_TABLE_NAME | Nom de table dupliqué |
| RELATION_TARGET_MISSING | Relation vers instance inexistante |
| MISSING_PRIMARY_KEY | Entité sans clé primaire |
| CYCLIC_RELATION | Cycle dans les relations |
| FIELD_TYPE_MISMATCH | Type de valeur par défaut incompatible |
| UNSAT_CORE | Contrainte violée (unsat core Z3) |
