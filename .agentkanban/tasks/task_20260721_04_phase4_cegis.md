---
title: "Phase 4 — Boucle CEGIS minimale"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Synthèse inductive via LLM local + vérification SMT/tests.
  Interfaces : SynthesisProblem, CandidateGenerator, CandidateVerifier,
  CounterExampleReducer, CounterExampleStore, CegisCoordinator.
  Applications : patches AST, templates, règles, contraintes SMT.
---

## Contexte

Issu de l'analyse détaillée du dépôt (commit 9941bb8).
Commencer seulement après les Phases 1–3 stabilisées.
Le but n'est pas d'ajouter ILP, génétique, DreamCoder et MCTS immédiatement,
mais de créer d'abord les interfaces avant de brancher des moteurs spécialisés.

Référence : sections 7, 9.4, 10 de l'analyse.

## TODOs

### interfaces de synthèse (7.1)

- [ ] Créer `SynthesisProblem(BaseModel)` avec : id, target_kind, specification, examples, counterexamples, search_space, constraints, budget
- [ ] Créer `CandidateKind` : enum discriminante (patch, template, rule, smt_constraint)
- [ ] Créer `Specification` : conteneur pour la spécification formelle du problème
- [ ] Créer `SearchSpace` : bornes du domaine de recherche
- [ ] Créer `SearchBudget` : max_iterations, timeout, max_candidates

### CandidateGenerator (7.2)

- [ ] Créer le protocol `CandidateGenerator` avec `generate(problem, context) → Sequence[Candidate]`
- [ ] Implémenter `LlmCandidateGenerator` : utilise un LLM local pour générer des candidats
- [ ] Créer `Candidate(BaseModel)` avec : id, program, kind, score optionnel, métadonnées
- [ ] Ajouter un test : `LlmCandidateGenerator.generate()` retourne des candidats bien formés

### CandidateVerifier (7.3)

- [ ] Créer le protocol `CandidateVerifier` avec `verify(candidate, problem) → VerificationResult`
- [ ] Implémenter `SchemaVerifier` : vérifie la conformité au schéma du candidat
- [ ] Implémenter `SmtVerifier` : utilise Z3 pour vérifier le candidat
- [ ] Implémenter `AstVerifier` : vérifie la syntaxe AST
- [ ] Implémenter `LintVerifier` : exécute le linter sur le candidat
- [ ] Implémenter `TypecheckVerifier` : exécute le typechecker
- [ ] Implémenter `TestVerifier` : exécute les tests sur le candidat
- [ ] Implémenter `GoldenVerifier` : compare avec les golden tests
- [ ] Créer `VerificationResult` : valid (bool), failures (list[VerificationFailure]), metrics
- [ ] Ajouter un test : chaque vérificateur retourne le bon résultat pour un candidat valide/invalide

### CounterExampleReducer (7.4)

- [ ] Créer le protocol `CounterExampleReducer` avec `minimize(failure) → CounterExample`
- [ ] Implémenter `MinimalCounterExampleReducer` : minimise le contre-exemple (delta debugging)
- [ ] Créer `CounterExample(BaseModel)` : inputs, expected_output, actual_output, diagnostic
- [ ] Créer `VerificationFailure(BaseModel)` : kind, location, message, context
- [ ] Ajouter un test : le réducteur produit un contre-exemple minimal

### CounterExampleStore (7.5)

- [ ] Créer le protocol `CounterExampleStore` avec `append(ce)`, `find_similar(query) → Sequence[CounterExample]`
- [ ] Implémenter `JsonlCounterExampleStore` : stockage JSONL
- [ ] Créer `CounterExampleQuery` : filters sur kind, predicate, plage de dates
- [ ] Ajouter un test : CE stocké puis retrouvé par similarité
- [ ] Ajouter un test : déduplication des CE identiques

### CegisCoordinator (7.6)

- [ ] Créer `CegisCoordinator` avec la boucle principale :
  - `generator.generate(problem)`
  - `verifier.verify(candidate, problem)`
  - si valide → `SynthesisResult.success(candidate)`
  - si invalide → `reducer.minimize(failure)` → `store.append(ce)` → itérer
- [ ] Créer `SynthesisResult(BaseModel)` : success | exhausted | timeout | error
- [ ] Gérer le budget : max_iterations, timeout
- [ ] Ajouter un test : boucle CEGIS avec faux générateur/vérificateur (cycle contrôlé)
- [ ] Ajouter un test : la boucle s'arrête après épuisement du budget

### SynthesisContext

- [ ] Créer `SynthesisContext` : regroupe les dépendances (store, observabilité, scheduler)
- [ ] Injecter le contexte dans le générateur et le vérificateur

### premières applications

- [ ] Appliquer la boucle CEGIS aux **patches AST** : patch incorrect → diagnostic → contre-exemple minimal → correction LLM → non-régression
- [ ] Appliquer aux **templates Jinja** : template qui ne compile pas → correction
- [ ] Appliquer aux **règles d'inférence** : règle incorrecte → contre-exemple → correction
- [ ] Appliquer aux **contraintes SMT** : contrainte UNSAT → diagnostic
- [ ] Ajouter un test de bout en bout : patch AST incorrect → correction automatique

## Conversation

### user

Créer les tickets pour chaque phase de l'analyse détaillée du dépôt LOF-Framework.
