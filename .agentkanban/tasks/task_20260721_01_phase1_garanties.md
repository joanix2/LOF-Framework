---
title: "Phase 1 — Rendre vraies les garanties annoncées"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Priorité absolue : atomicité, sécurité, vrai `lof check`, vrai test d'indépendance,
  vrai `lof dev`, options CLI actives, bug contradictions, typage CI bloquant.
---

## Contexte

Issu de l'analyse détaillée du dépôt (commit 9941bb8).
Tant que ces garanties ne sont pas strictement vraies, n'ajouter aucun nouvel algorithme inductif.

Référence : sections 3.1–3.8, 9.1 de l'analyse.

## TODOs

### compilation atomique (3.1)

- [ ] Créer un répertoire de staging `.lof/staging/<compilation-id>/` pour le rendu
- [ ] Séparer `compile()` en phases : `plan` → `render` → `validate` → `commit`
- [ ] Utiliser `os.replace(staging_generated, final_generated)` pour le commit atomique
- [ ] En cas d'échec, ne jamais altérer `generated/`
- [ ] Ajouter un test : échec d'instance N → instances 1..N-1 non écrites

### validation des chemins (3.2)

- [ ] Créer `ArtifactPath.resolve_inside(output_root)` avec invariant `resolved.is_relative_to(output_root.resolve())`
- [ ] Interdire les chemins absolus dans `copy_file`
- [ ] Interdire `..`, liens symboliques sortants, collisions de casse, chemins réservés
- [ ] Ajouter un test : `output_pattern` malveillant `../../outside.py` est rejeté
- [ ] Ajouter un test : chemin absolu est rejeté

### vrai `lof check` (3.3)

- [ ] Créer `CheckReport(BaseModel)` avec champs structurés : structural, semantic, compilation, backend_lint, backend_typecheck, backend_tests, frontend_lint, frontend_typecheck, frontend_tests
- [ ] Étendre `Project.check()` pour exécuter Ruff, Pyright, tsc, pytest, vitest sur le projet généré
- [ ] Réserver le message "All checks passed" au cas où tous les gates activés ont réussi
- [ ] Ajouter un test : `lof check` détecte une erreur volontaire dans le projet généré

### vrai test d'indépendance (3.3, 5)

- [ ] Remplacer le simple grep par une assertion bloquante
- [ ] Tester que le projet généré s'installe, démarre, compile, passe ses tests
- [ ] Ajouter un test CI : environnement vierge sans LOF, installation du projet généré, `make test`

### vrai `lof dev` ou documentation honnête (3.4)

- [ ] Choisir : renommer en `lof dev --print-commands` OU créer un vrai process manager
- [ ] Si process manager : lance API + frontend, relaye logs, Ctrl+C clean, propagation codes d'erreur
- [ ] Ajouter un test : `lof dev` démarre et s'arrête proprement

### options CLI inactives (3.5)

- [ ] Supprimer `--instance`, `--type`, `--force` de la CLI ou les connecter réellement au `Compiler`
- [ ] Ajouter un test : `--instance` ne compile que l'instance spécifiée
- [ ] Ajouter un test : `--type` filtre par type
- [ ] Ajouter un test : `--force` force la recompilation
- [ ] Supprimer `--dry-run` ou l'implémenter vraiment

### bug de contradictions (3.7)

- [ ] Corriger `_detect_contradictions` : arrêter d'ignorer les `rejected` avant de chercher les `rejected`
- [ ] Créer deux dimensions : `truth: positive | negative` et `epistemic_status: asserted | inferred | hypothesized | rejected`
- [ ] Ajouter un test : règle A ∧ ¬A détectée comme contradiction
- [ ] Ajouter un test : fait asserté + fait rejeté sur même prédicat = contradiction

### typage bloquant en CI (5)

- [ ] Remplacer `pyright src/lof || true` (Makefile) par `pyright src/lof` sans `|| true`
- [ ] Ajouter Pyright au workflow GitHub Actions (pas seulement au Makefile)
- [ ] Ajouter un test CI : une erreur de type volontaire fait échouer la CI

### `lint` ne doit pas modifier les fichiers (5)

- [ ] Créer deux cibles Makefile : `lint` (vérifie) et `lint-fix` (corrige)
- [ ] CI doit appeler `lint`, pas `lint-fix`
- [ ] `make ci` ne doit plus utiliser `ruff check --fix`

### docs et URLs

- [ ] Corriger les URLs dans `pyproject.toml` : remplacer `github.com/graphify-labs/lof` par `github.com/joanix2/LOF-Framework`
- [ ] Mettre à jour les commandes d'installation dans le README tant que le package n'est pas sur PyPI
- [ ] Remplacer ou supprimer la mention "25 inference rules" non vérifiée

## Conversation

### user

Créer les tickets pour chaque phase de l'analyse détaillée du dépôt LOF-Framework.
