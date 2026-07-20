# Changelog

## 0.2.0 — 2026-07-20

### Architecture

- Pipeline neuro-symbolique complète : Bronze → Silver → Reasoning → Gold → SMT → Compilation
- Datalog fixpoint engine avec 25 règles (permissions, projections, UI)
- Validation sémantique SMT avec Z3 avant toute génération
- Graphe de contexte pour templates (TemplateGraphView)

### Modules

- `bronze/` : stockage append-only des expressions brutes
- `silver/` : extraction sémantique spaCy + graphe ouvert
- `reasoning/` : moteur Datalog à point fixe avec provenance
- `validation/smt/` : 8 compilateurs de contraintes + solver Z3
- `graph/` : graphes de types, instances, contexte de projection
- `compilation/` : pipeline Jinja + patches LibCST

### Refactoring

- `domain/` : errors, settings, ports, pipeline_stage
- `interfaces/` : CLI découpée par domaine (bronze, silver, gold, reason, constraints)
- `infrastructure/` : adaptateurs Z3 derrière SemanticSolverPort
- Suppression du duplicate rendering/context_resolver.py

### Profil FastAPI + React

- 27 types, 48 instances → 48 fichiers générés
- Backend : FastAPI, SQLAlchemy, Pydantic v2, tests pytest
- Frontend : React, TanStack Query, React Hook Form
- OpenAPI → SDK TypeScript
- Docker Compose

### Tests

- 75 tests framework
- 33 tests backend générés
- 12 scénarios LOP-Bench (6 valides + 6 invalides)

## 0.1.0 — 2026-07-19

- Structure initiale du méta-framework
- Modèles Pydantic (types, instances, patches, cibles)
- Graphe NetworkX avec détection de cycles
- Rendu Jinja avec filtres de nommage
- Patches AST avec LibCST
- CLI Typer
- Bazel Bzlmod
