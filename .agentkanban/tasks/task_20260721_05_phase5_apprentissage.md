---
title: "Phase 5 — Apprentissage inductif"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Moteurs inductifs spécialisés branchés sur l'infrastructure CEGIS :
  énumération DSL, ILP règles, SMT sketches, génétique, mémoire
  de réparation, anti-unification, promotion de macros.
---

## Contexte

Issu de l'analyse détaillée du dépôt (commit 9941bb8).
Phase 5 seulement après Phases 1–4 stabilisées.
Ne pas implémenter tous les moteurs d'un coup — l'infrastructure CEGIS
(Phase 4) doit d'abord être solide. Chaque moteur est un
`CandidateGenerator` supplémentaire branché sur la même boucle.

Référence : sections 7, 9.5, 10 de l'analyse.

## TODOs

### énumération pour petits DSL

- [ ] Créer `EnumerativeCandidateGenerator(CandidateGenerator)` : énumération exhaustive bornée
- [ ] Définir la grammaire du DSL cible (profondeur max, types autorisés)
- [ ] Implémenter l'énumération par taille de programme croissante
- [ ] Ajouter un test : génération de tous les programmes valides de taille ≤ 3

### ILP pour règles

- [ ] Créer `IlpCandidateGenerator(CandidateGenerator)` : apprentissage de règles Datalog
- [ ] Implémenter un algorithme ILP simple (FOIL ou dérivé)
- [ ] Support des exemples positifs et négatifs
- [ ] Généralisation : spécialisation vs généralisation
- [ ] Ajouter un test : apprendre une règle simple à partir d'exemples
- [ ] Ajouter un test : l'ILP ne produit pas de règle contradictoire avec les contraintes SMT

### solveur de sketches SMT

- [ ] Créer `SmtSketchGenerator(CandidateGenerator)` : complétion de sketches Z3
- [ ] Définir le format de sketch : programme avec trous `?`
- [ ] Utiliser Z3 pour remplir les trous
- [ ] Ajouter un test : sketch avec 2 trous → solution complète

### algorithme génétique

- [ ] Créer `GeneticCandidateGenerator(CandidateGenerator)` : évolution de programmes
- [ ] Définir les opérateurs : croisement, mutation, sélection
- [ ] Définir la fonction de fitness (basée sur les vérificateurs)
- [ ] Ajouter un test : évolution d'un programme simple sur 10 générations

### mémoire de réparation

- [ ] Créer `RepairMemory` : stocke les paires (programme_erroné, programme_corrigé, contexte)
- [ ] Implémenter la recherche par similarité structurelle
- [ ] Utiliser la mémoire comme candidat prioritaire dans la boucle CEGIS
- [ ] Ajouter un test : une réparation précédente est réutilisée pour un problème similaire

### anti-unification

- [ ] Implémenter l'anti-unification pour deux programmes ou plus
- [ ] Généraliser deux exemples en un programme paramétré
- [ ] Ajouter un test : anti-unification de `f(x) = x + 1` et `f(y) = y + 2` → `f(z) = z + ?`

### promotion de macros

- [ ] Détecter les sous-programmes fréquents dans les candidats générés
- [ ] Promouvoir les motifs fréquents en macros du DSL
- [ ] Ajouter un test : un sous-programme répété 3 fois est promu en macro

### intégration dans la boucle CEGIS

- [ ] Branchable sur `CegisCoordinator` (Phase 4) comme `CandidateGenerator` spécialisé
- [ ] `CegisCoordinator` peut combiner plusieurs générateurs (LLM + énumératif + génétique)
- [ ] Stratégie de sélection : prioriser LLM, puis repair memory, puis génétique, puis énumération
- [ ] Ajouter un test : boucle CEGIS avec 2 générateurs différents

### benchmark inductif

- [ ] Créer un benchmark de synthèse : problèmes avec spécification, exemples, contre-exemples
- [ ] Mesurer : taux de succès, temps moyen, itérations moyennes par générateur
- [ ] Ajouter au CI (optionnel, non bloquant au début)

## Conversation

### user

Créer les tickets pour chaque phase de l'analyse détaillée du dépôt LOF-Framework.
