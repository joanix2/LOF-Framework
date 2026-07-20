# Architecture : chaîne de compilation neuro-symbolique

```
Expression utilisateur
        ↓
BRONZE — données brutes, tickets, messages
        ↓ extraction sémantique (spaCy NER + dépendances)
SILVER — graphe sémantique ouvert avec provenance
        ↓ raisonnement logique (Datalog fixpoint)
GRAPHE ENRICHI — faits explicites + inférés + contradictions
        ↓ matérialisation (sélection et fermeture)
GOLD — DSL canonique décrivant l'application
        ↓ validation structurelle (JSON Schema / Pydantic)
        ↓ validation sémantique (SMT / Z3)
   SAT ?
   ├── NON → diagnostic pour LLM → retour Silver/Gold
   └── OUI → compilation
              ↓ templates Jinja + patches AST
              PROGRAMME GÉNÉRÉ (FastAPI + React + SQL)
              ↓ validation statique (ruff, tsc, prettier)
              ↓ validation dynamique (pytest, vitest, Playwright)
              PROJET VALIDÉ
```

## Couches

| Couche | Rôle | Technologie |
|--------|------|-------------|
| **Bronze** | Mémoire exacte des expressions brutes (append-only) | JSON, `bronze/store.py` |
| **Silver** | Graphe sémantique ouvert avec provenance | spaCy, `silver/graph.py` |
| **Platinum** | Inférences logiques, règles, explications | Datalog, `reasoning/engine.py` |
| **Gold** | DSL applicatif fermé et décidé | JSON, `reasoning/gold_materializer.py` |
| **SMT** | Validation de cohérence | Z3, `validation/smt/solver.py` |
| **Compilation** | Projection templates + patches AST | Jinja2 + LibCST, `compilation/` |
| **Validation** | Lint, types, tests | Ruff, pyright, pytest, vitest |

## Principes

- **Bronze** = ce qui a réellement été dit (append-only)
- **Silver** = ce que le système croit avoir compris (monde ouvert)
- **Gold** = ce que le compilateur doit construire (monde fermé)
- **LLM** peut créer/modifier : tickets, règles, types, instances, templates, patches
- **LLM** ne modifie jamais : Bronze historique, fichiers générés, SDK, diagnostics

## Pipeline formel

```
Program =
ValidateRuntime(
  ValidateStatic(
    Rewrite(
      SMTValidate(
        Materialize(
          Infer(
            Extract(Bronze),
            Rules
          )
        )
      ),
      Templates,
      Patches
    )
  )
)
```
