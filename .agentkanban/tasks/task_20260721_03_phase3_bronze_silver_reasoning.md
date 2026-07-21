---
title: "Phase 3 — Stabiliser Bronze, Silver et Reasoning"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Identifiants déterministes, entités référencées par ID, modèle
  vérité/statut épistémique, négation explicite, open/closed world,
  indexation Datalog, semi-naive evaluation, contradictions, profils
  versionnés, tests de provenance.
---

## Contexte

Issu de l'analyse détaillée du dépôt (commit 9941bb8).

Référence : sections 3.7–3.12, 9.3 de l'analyse.

## TODOs

### identifiants déterministes (3.10)

- [ ] Remplacer `uuid4()` dans l'extracteur Silver par des identifiants dérivés de `sha256(bronze_id + start + end + label)`
- [ ] Rendre les identifiants de claims déterministes : `sha256(subject_id + predicate + object_id + provenance)`
- [ ] Ajouter un test : deux extractions du même ticket produisent les mêmes identifiants

### entités référencées par ID (3.12)

- [ ] Les relations Silver doivent utiliser `subject_entity_id` et `object_entity_id` au lieu des noms
- [ ] Conserver les mentions textuelles originales (surface forms) à côté des IDs
- [ ] Ajouter un test : résolution d'entité par ID après extraction

### normalisation sémantique non destructive (3.11)

- [ ] Séparer `surface_form`, `canonical_label`, `normalized_key` dans les entités
- [ ] Préserver les termes techniques : FastAPI, OAuth, SQLAlchemy, etc.
- [ ] Ajouter un test : les acronymes et noms propres ne sont pas dégradés par la normalisation

### modèle vérité / statut épistémique (3.7)

- [ ] Créer deux dimensions distinctes : `truth: positive | negative` et `epistemic_status: asserted | inferred | hypothesized | rejected`
- [ ] Migrer les faits existants vers le nouveau modèle
- [ ] Ajouter un test : un fait peut être `positive + hypothesized` ou `negative + asserted`

### négation explicite (3.8)

- [ ] Implémenter `not_explicit(P)` : recherche d'un fait négatif dans la base
- [ ] Implémenter `not_closed(P)` : absence autorisée seulement sur prédicat fermé
- [ ] Documenter la sémantique de négation (open-world par défaut)
- [ ] Remplacer le `return None` immédiat de `_match_condition()` pour `cond.negated`
- [ ] Ajouter un test : règle avec `not_explicit(P)` matche correctement

### prédicats open/closed world (3.8)

- [ ] Définir un registre de prédicats avec leur statut de clôture
- [ ] Par défaut : open-world (absence ≠ négation)
- [ ] Ajouter un test : absence sur prédicat ouvert → pas d'inférence négative
- [ ] Ajouter un test : absence sur prédicat fermé → inference négative

### détection correcte des contradictions (3.7)

- [ ] Corriger `_detect_contradictions` : ne pas filtrer les `rejected` avant la détection
- [ ] Un groupe de faits identiques avec `positive + asserted` et `negative + asserted` = contradiction
- [ ] Un groupe avec `positive + inferred` et `positive + rejected` = pas une contradiction (rejet administratif)
- [ ] Ajouter un test : `asserted(A)` et `not asserted(A)` → contradiction
- [ ] Ajouter un test : `inferred(A)` et `rejected(A)` → pas contradiction

### indexation du moteur Datalog (3.9)

- [ ] Créer un index des faits par prédicat
- [ ] Utiliser l'index dans `evaluate()` (actuellement inutilisé)
- [ ] Ajouter un test : l'index accélère l'évaluation (benchmark)

### semi-naive evaluation (3.9)

- [ ] Implémenter l'évaluation semi-naïve : ne considérer que les faits nouveaux à chaque itération
- [ ] Ajouter un test : même résultats qu'avec l'évaluation naïve
- [ ] Ajouter un test : temps d'exécution amélioré

### déduplication robuste

- [ ] Garantir l'absence de doublons dans la base de faits
- [ ] Utiliser une structure ensembliste dédiée (pas de liste simple)
- [ ] Ajouter un test : une règle qui produit deux fois le même fait ne le duplique pas

### analyse statique des règles

- [ ] Détecter les variables non liées dans les règles
- [ ] Détecter les règles dangereuses (non stratifiables)
- [ ] Ajouter un test : règle avec variable non liée → erreur de validation
- [ ] Ajouter un test : règle non stratifiable → erreur de validation

### profils de règles versionnés

- [ ] Ajouter un numéro de version aux profils de règles
- [ ] Journaliser les changements de profil
- [ ] Ajouter un test : chargement de profil avec version

### tests de provenance (2.7)

- [ ] Vérifier que les `bronze_ids` sont correctement propagés des faits sources aux faits dérivés
- [ ] Vérifier que `InferenceTrace` contient règle, bindings, sources et itération
- [ ] Ajouter un test : provenance complète tracée pour une inférence à 3 sauts
- [ ] Ajouter un test : modification d'un fait source invalide les faits dérivés correspondants

### statistiques par règle

- [ ] Ajouter des compteurs : nombre de matchs, de produits, durée par règle
- [ ] Exposer les statistiques via l'API de diagnostic
- [ ] Ajouter un test : les statistiques sont non-nulles après une évaluation

## Conversation

### user

Créer les tickets pour chaque phase de l'analyse détaillée du dépôt LOF-Framework.
