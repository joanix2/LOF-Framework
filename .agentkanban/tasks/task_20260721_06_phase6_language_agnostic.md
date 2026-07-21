---
title: "Phase 6 — Framework langage-agnostique (suppression des dépendances Python/TS)"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Rendre le framework LOF capable de générer des projets dans n'importe
  quel langage cible. Supprimer les hardcodages Python/TypeScript dans le
  coeur du framework : AST, pipeline, validation, CLI, profiles, settings.
  Extraire les spécificités langage dans des plugins/adapters externes.
---

## Contexte

Analyse détaillée du dépôt (commit 9941bb8). Le framework est actuellement
câblé en dur sur Python (FastAPI) et TypeScript (React). Tout nouveau langage
cible nécessite des modifications dans le code coeur. L'objectif est de
rendre le noyau du framework complètement indépendant du langage cible.

## Architecture cible

```
src/lof/
├── core/                    # Noyau pur, zéro référence à un langage
│   ├── project.py
│   ├── compiler.py
│   ├── pipeline.py
│   └── ...
├── ast/
│   ├── adapter.py           # Protocol/ABC pur
│   └── adapters/            # Implémentations par langage (plugins)
│       ├── python_libcst.py
│       └── typescript_tsmorph.py
├── validation/              # Valideurs par langage (plugins)
│   ├── registry.py
│   └── backends/
│       ├── python_validator.py
│       ├── typescript_validator.py
│       └── ...
├── profiles/                # Profiles non liés à un langage
│   ├── registry.py
│   ├── fastapi_react/
│   └── mobile_field/
└── cli.py                   # CLI générique, lit le profil actif
```

Tout ce qui est langage-spécifique doit être :
- soit dans un profil (déclaratif)
- soit dans un adaptateur (plugin Python)
- soit dans des templates et définitions (fichiers utilisateur)

Rien dans `core/` ne doit référencer `python`, `typescript`, `fastapi`, `react`.

## TODOs

### Noyau : supprimer les hardcodages langage dans Pipeline

- [ ] `pipeline.py:_get_language()` — Remplacer le fallback `return "python"` par `raise ValueError("unknown language")` ou `return "unknown"`
- [ ] `pipeline.py:_resolve_output_path()` — Ne pas avaler silencieusement les exceptions Jinja (actuellement `except Exception: pass`)
- [ ] Vérifier que le `language` provient toujours du `target.language` dans la définition de cible, jamais d'un défaut codé en dur
- [ ] Ajouter un test : type sans `language` dans sa target → erreur explicite, pas fallback silencieux

### Noyau : supprimer les hardcodages langage dans CLI

- [ ] `cli.py:dev()` — Remplacer les chemins durs `apps/api` et `apps/web` par une configuration lue depuis le profil ou le manifeste
- [ ] `cli.py:dev()` — Remplacer `uvicorn` et `npm run dev` par des commandes lues depuis la config du projet généré
- [ ] `cli.py:init()` — Remplacer les dossiers `templates/python`, `templates/typescript`, `patches/python`, `patches/typescript` par des dossiers génériques ou lus depuis le profil
- [ ] `cli.py:profiles()` — Lire la liste depuis `ProfileRegistry`, pas de ligne codée en dur
- [ ] `cli.py:new()` — Remplacer le défaut `"fastapi-react"` par `None` (obliger l'utilisateur à spécifier un profil, ou détecter depuis l'environnement)
- [ ] Ajouter un test : `lof dev` avec un profil non-web (ex: CLI tool) ne mentionne pas `uvicorn` ou `npm`

### Noyau : supprimer les hardcodages langage dans le profile registry

- [ ] `profiles/__init__.py` — Remplacer le dictionnaire codé en dur par un `ProfileRegistry` qui scanne un répertoire de profils
- [ ] `profiles/__init__.py` — Remplacer le défaut `"fastapi-react"` par un paramètre obligatoire
- [ ] Rendre les profils découvrables : `profiles/*/profile.yaml` ou `profiles/*.yaml`
- [ ] Ajouter un test : un profil déposé dans `profiles/` est automatiquement détecté

### Noyau : supprimer les hardcodages langage dans Settings

- [ ] `domain/settings.py:default_profile` — Rendre optionnel, pas de défaut codé en dur
- [ ] Vérifier que tous les composants utilisent `settings.default_profile` ou le paramètre explicite, jamais une chaîne littérale `"fastapi-react"`

### AST : rendre le système d'adaptateurs extensible sans modifier le code

- [ ] `ast/patch_engine.py` — Rendre le registre d'adaptateurs injectable (constructeur ou setter), pas de dictionnaire codé en dur
- [ ] Supprimer l'import direct de `PythonLibCstAdapter` dans `patch_engine.py` (utiliser un registre ou une factory)
- [ ] Créer un mécanisme d'enregistrement : `AstAdapterRegistry.register("python", PythonLibCstAdapter())`
- [ ] Ajouter un test : un adaptateur personnalisé peut être enregistré sans modifier le code source du framework
- [ ] Implémenter l'adaptateur TypeScript (stub actuel dans `typescript_tsmorph.py`)
- [ ] Ajouter un test : `PatchEngine.apply_patches(language="typescript", ...)` fonctionne

### Validation : rendre les vérificateurs extensibles par langage

- [ ] `artifact_validator.py` — Remplacer les hardcodages `apps/api` et `apps/web` par des chemins lus depuis le manifeste ou la target
- [ ] Créer un `ValidatorRegistry` : chaque langage enregistre son validateur (ruff, prettier, eslint, gofmt, etc.)
- [ ] Implémenter `TypeScriptValidator` (remplacer le `pass` actuel)
- [ ] Rendre les validateurs appelables depuis la target definition : `target.validators = ["ruff", "pytest"]`
- [ ] Ajouter un test : validation dynamique basée sur la target, pas sur des chemins durs

### Noyau : chaînes littérales éparses

- [ ] `reasoning/gold_materializer.py` — Remplacer `"entity-model"` codé en dur par le type_id lu depuis le profil
- [ ] `reasoning/gold_materializer.py` — Remplacer `ent["name"] + "s"` (pluralisation anglaise) par une fonction de pluralisation paramétrable
- [ ] `bench/runner.py` — Remplacer `"python-module"` par la target du profil actif
- [ ] `commands/new_project.py` — Remplacer les ignores `.venv/`, `__pycache__/`, `node_modules/` par des ignores lis depuis le profil
- [ ] Ajouter un test : `lof new --profile minimal` ne crée pas de répertoire Python/TS spécifique

### CLI : `lof check` doit être générique

- [ ] `cli.py:check()` — Lancer les validateurs du profil actif, pas seulement Python
- [ ] Afficher un rapport structuré (cf Phase 1) listant chaque langage validé
- [ ] Ajouter un test : `lof check` avec un profil Go lance `gofmt`, pas `ruff`

### Cibles (targets) : séparer la définition du langage

- [ ] Ajouter un champ `validators: list[str]` dans le schéma target (ex: `["ruff", "pytest"]`)
- [ ] Ajouter un champ `dev_command: str` dans la target (ex: `"uvicorn app.main:app --reload"`)
- [ ] Ajouter un champ `build_command: str` dans la target
- [ ] Ajouter un champ `check_command: str` dans la target
- [ ] Supprimer la dépendance à `libcst` du coeur (extra optionnel dans pyproject.toml)
- [ ] Ajouter un test : une target Go complète peut être définie sans modifier le code
- [ ] Ajouter un test : `compile()` avec target Go produit des fichiers `.go`

### Dépendances et packaging

- [ ] `pyproject.toml` — Remplacer la description "FastAPI+React" par "generative DSL framework"
- [ ] `pyproject.toml` — Déplacer `libcst` en dépendance optionnelle (extra `python-ast`)
- [ ] `pyproject.toml` — Déplacer les outils TypeScript/Prettier dans un extra optionnel
- [ ] `pyproject.toml` — Mettre à jour les keywords pour ne pas citer FastAPI/React
- [ ] Ajouter un test : installation minimale (`pip install lof-framework`) sans extras ne dépend pas de libcst

## Conversation

### user

créer une phase 6 pour rendre le framework agnostique des langages cibles — pas de dépendance à python ou ts.
