# Architecture du LOP Framework

## Pipeline

```
Bronze (tickets bruts, append-only)
  → Silver (extraction sémantique spaCy)
  → Reasoning (inférence Datalog à point fixe)
  → Gold (DSL applicatif canonique)
  → SMT validation (Z3)
  → Compilation (Jinja + patches AST)
  → Projet généré (FastAPI + React)
  → Linters + tests
```

## Couches

| Couche | Technologie | Responsabilité |
|--------|-------------|----------------|
| Bronze | JSON, append-only | Mémoire exacte des expressions utilisateur |
| Silver | spaCy NER + dépendances | Graphe sémantique ouvert avec provenance |
| Reasoning | Datalog fixpoint | Inférences logiques, règles, explications |
| Gold | JSON, Pydantic | DSL canonique fermé et décidé |
| SMT | Z3 | Validation de cohérence avant génération |
| Compilation | Jinja2 + LibCST | Projection templates + patches AST |
| Validation | Ruff, pytest, vitest | Lint, typage, tests du projet généré |

## Principes fondamentaux

- **Bronze** = ce qui a réellement été dit (append-only)
- **Silver** = ce que le système croit avoir compris (monde ouvert)
- **Gold** = ce que le compilateur doit construire (monde fermé)
- Le moteur logique **enrichit** le modèle ; le SMT **valide** la cohérence
- Aucune génération après UNSAT ou UNKNOWN
- Les fichiers générés ne sont jamais la source de vérité
