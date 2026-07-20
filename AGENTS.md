# LOP Framework — Règles de programmation orientée langage

## Sources de vérité

Les agents peuvent modifier :
- `definitions/types/` — définitions de types
- `instances/` — instances d'entités
- `templates/` — templates Jinja
- `patches/` — patches AST
- `schemas/` — schémas JSON
- `definitions/targets/` — cibles
- `framework/src/lof/reasoning/profiles/` — règles d'inférence
- `benchmarks/` — scénarios de benchmark
- `tests/` — tests

Les agents ne doivent **jamais** modifier directement :
- `generated/`
- `generated-project/`
- `data/` (sauf via `lof bronze add`)
- Les diagnostics dans `.lof/`
- Le SDK OpenAPI généré

## Pipeline

```
Bronze (tickets bruts, append-only)
  → Silver (extraction sémantique spaCy)
  → Reasoning (inférence Datalog)
  → Gold (DSL applicatif)
  → SMT validation (Z3)
  → Compilation (Jinja + patches AST)
  → Projet généré
  → Linters + tests
```

## Avant chaque modification

1. Identifier la couche concernée (Bronze/Silver/Reasoning/Gold/SMT/Compilation)
2. Rechercher une abstraction existante dans `domain/` ou `infrastructure/`
3. Vérifier les duplications possibles
4. Localiser les tests existants
5. Ajouter un test de caractérisation si nécessaire

## Règles

- Une fonction = une responsabilité
- Pas de logique métier dans les templates Jinja
- Pas de contournement de la validation SMT
- Pas de modification des fichiers générés
- Pas de valeurs métier en dur (utiliser `domain/settings.py`)
- Signatures typées pour toutes les APIs publiques
- `make format && make lint && make typecheck && make test` après chaque modification
