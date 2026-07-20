# Code Review — LOP Framework

Date: 2026-07-20
Commit: $(git rev-parse --short HEAD)

---

## 1. Arborescence actuelle

```
framework/src/lof/
├── cli.py                          (665 lignes — trop volumineux)
├── __init__.py
├── bronze/
│   ├── __init__.py
│   ├── models.py
│   └── store.py
├── compilation/
│   ├── __init__.py
│   ├── compiler.py
│   ├── manifest.py
│   ├── pipeline.py
│   └── writer.py
├── graph/
│   ├── __init__.py
│   ├── builder.py
│   ├── compiler_graph.py
│   ├── context_resolver.py
│   ├── instance_graph.py
│   ├── projection_context.py
│   └── validator.py
├── loading/
│   ├── __init__.py
│   ├── loader.py
│   └── registry.py
├── models/
│   ├── __init__.py
│   ├── artifact.py
│   ├── instance_definition.py
│   ├── patch_definition.py
│   ├── target_definition.py
│   └── type_definition.py
├── ast/
│   ├── __init__.py
│   ├── adapter.py
│   ├── patch_engine.py
│   ├── python_libcst.py
│   └── typescript_tsmorph.py
├── rendering/
│   ├── __init__.py
│   ├── context_resolver.py
│   └── jinja_renderer.py
├── reasoning/
│   ├── __init__.py
│   ├── engine.py
│   ├── explanation.py
│   ├── fact_encoder.py
│   ├── gold_materializer.py
│   ├── integration.py
│   └── profiles/
│       ├── __init__.py
│       └── fastapi_react.py
├── silver/
│   ├── __init__.py
│   ├── extractor.py
│   ├── gold_builder.py
│   ├── graph.py
│   └── models.py
├── utils/
│   ├── __init__.py
│   ├── hashing.py
│   ├── naming.py
│   └── paths.py
└── validation/
    ├── __init__.py
    ├── diagnostics.py
    ├── schema_validator.py
    ├── semantic_validator.py
    └── smt/
        ├── __init__.py
        ├── constraint_definition.py
        ├── context.py
        ├── solver.py
        ├── validation_engine.py
        └── compilers/
            ├── __init__.py
            ├── acyclic_relation.py
            ├── cardinality_compatible.py
            ├── dependency_satisfied.py
            ├── field_type_compatible.py
            ├── operation_requires.py
            ├── registry.py
            ├── relation_target.py
            ├── required_property.py
            └── unique_property.py
```

## 2. Responsabilités des modules

| Module | Responsabilité | Problèmes |
|--------|---------------|-----------|
| `cli.py` | CLI Typer, 9+ command groups | **665 lignes**, contient aussi des helpers |
| `bronze/` | Stockage append-only | Correct, bien séparé |
| `compilation/` | Orchestration, pipeline, manifeste | `compiler.py` et `pipeline.py` ont des responsabilités qui se chevauchent |
| `graph/` | Graphes types, instances, contexte | `instance_graph.py` fait à la fois graphe ET requêtes |
| `models/` | Pydantic models | Correct, bien séparé |
| `ast/` | Adaptateurs AST | `typescript_tsmorph.py` est un stub non implémenté |
| `rendering/` | Jinja + résolution contexte | OK |
| `reasoning/` | Moteur Datalog + matérialisation Gold | `gold_materializer.py` mélange inférence et écriture |
| `silver/` | Graphe sémantique | `extractor.py` dépend de spaCy directement |
| `validation/` | JSON Schema + Sémantique + SMT | `solver.py` trop gros (70 lignes), `validation_engine.py` 99 lignes |
| `utils/` | Utilitaires | OK, bien factorisé |

## 3. Dépendances entre modules

```
cli.py → compilation/, graph/, loading/, validation/smt/, bronze/, silver/, reasoning/
compilation/ → graph/, loading/, rendering/, ast/, validation/
graph/ → models/, loading/, validation/
loading/ → models/
models/ → (pures — aucune dépendance framework)
rendering/ → utils/, models/
reasoning/ → silver/, models/
silver/ → bronze/, models/
validation/ → models/, graph/, loading/
```

**Problème** : `cli.py` importe **tous les modules** — pas de séparation interface/application.

## 4. Duplications identifiées

| Problème | Fichiers | Priorité |
|----------|----------|----------|
| Construction de contexte Jinja | `rendering/context_resolver.py` + `graph/context_resolver.py` | Critique |
| Logique de résolution de chemin de sortie | `pipeline.py` + `compiler.py` | Important |
| Parsing JSON avec mapping camelCase | `loading/loader.py` (3 méthodes similaires) | Important |
| Validation de graphe | `graph/validator.py` + `validation/semantic_validator.py` | Important |
| Diagnostics | `validation/diagnostics.py` + modèles séparés dans SMT | Amélioration |
| Requêtes de graphe `reachable` | `graph/instance_graph.py` + `graph/projection_context.py` | Amélioration |

## 5. Valeurs en dur

| Valeur | Fichier | Priorité |
|--------|---------|----------|
| `"definitions/types"` | `loader.py:65` | Important |
| `"definitions/targets"` | `loader.py:86` | Important |
| `"instances"` | `loader.py:73` | Important |
| `"patches"` | `loader.py:79` | Important |
| Profondeur max graphe `3` | `graph/context_resolver.py` | Amélioration |
| Profondeur max `3` | `graph/projection_context.py` | Amélioration |
| `"fastapi-react"` | `cli.py` | Amélioration |
| Chemins de sortie `generated/` | `pipeline.py` | Important |
| Noms de profils | `reasoning/profiles/__init__.py` | Amélioration |

## 6. Fichiers trop volumineux

| Fichier | Lignes | Limite | Priorité |
|---------|--------|--------|----------|
| `cli.py` | 665 | 350 | Critique |
| `validation/smt/solver.py:validate()` | 70 | 50 | Important |
| `validation/smt/validation_engine.py:build_builtin_constraints()` | 99 | 50 | Important |
| `compilation/pipeline.py:process_instance()` | 68 | 50 | Important |
| `reasoning/engine.py:evaluate()` | 52 | 50 | Amélioration |
| `reasoning/gold_materializer.py:materialize()` | 58 | 50 | Amélioration |
| `graph/instance_graph.py:reachable()` | 57 | 50 | Amélioration |

## 7. Classes avec trop de responsabilités

| Classe | Problème | Priorité |
|--------|----------|----------|
| `Pipeline` | Résout contexte + rend + patch + écrit | Critique |
| `Compiler` | Charge + valide + compile | Important |
| `SilverGraph` | stockage + validation + recherche de contradictions | Amélioration |
| `GoldMaterializer` | Matérialisation + écriture fichier | Amélioration |
| `DatalogEngine` | Évaluation + matching + détection contradictions | Important |

## 8. Dépendances externes non isolées

| Dépendance | Utilisation directe dans | Priorité |
|------------|--------------------------|----------|
| spaCy | `silver/extractor.py` | Critique |
| Z3 | `validation/smt/solver.py` | Critique |
| NetworkX | `graph/builder.py`, `graph/instance_graph.py` | Important |
| Jinja2 | `rendering/jinja_renderer.py` | Important |
| LibCST | `ast/python_libcst.py` | Important |
| Typer | `cli.py` | Amélioration |

## 9. Fonctionnalités non opérationnelles

| Fonctionnalité | Problème | Priorité |
|---------------|----------|----------|
| Patches TypeScript | `typescript_tsmorph.py` est un stub | Important |
| Interface `SemanticSolver` (Protocol) | Défini dans `solver.py` mais pas utilisé comme port | Amélioration |
| `lof diff` | Implémentation partielle | Amélioration |
| `lof compile --instance` / `--type` | Options CLI déclarées mais non utilisées dans `compiler.py` | Important |
| `SchemaValidator` | Défini mais non utilisé dans le pipeline | Amélioration |

## 10. Priorisation des corrections

### Critique
1. `cli.py` — 665 lignes, découper par domaine
2. `Pipeline` — séparer contexte, rendu, patch, écriture
3. `silver/extractor.py` — isoler spaCy derrière un port
4. `validation/smt/solver.py` — isoler Z3 derrière un port
5. Duplication de résolution de contexte (`rendering/` vs `graph/`)

### Important
6. Chemins en dur dans `loader.py` — configurer via settings
7. `Compiler` — séparer chargement/validation/compilation
8. `lof compile --instance` / `--type` — implémenter ou retirer
9. Stub TypeScript — compléter ou documenter l'absence
10. `SchemaValidator` — intégrer ou retirer

### Amélioration
11. Profondeurs de graphe en dur — paramétriser
12. Template des messages de diagnostic — centraliser
13. `GoldMaterializer` — séparer logique et écriture
14. Tests de caractérisation manquants

## 11. Plan de correction

Les phases suivantes adressent ces problèmes par ordre de priorité décroissante.
