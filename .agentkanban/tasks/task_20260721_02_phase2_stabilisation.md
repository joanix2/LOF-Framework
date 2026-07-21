---
title: "Phase 2 — Stabiliser le framework"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Objets de résultats publics, ProjectContext, registre de profils,
  suppression structure legacy, vrai lof diff, compilation ciblée,
  manifestes déterministes, versionnement DSL, wheel TestPyPI.
---

## Contexte

Issu de l'analyse détaillée du dépôt (commit 9941bb8).
Phase 2 à entamer seulement après que les garanties de la Phase 1 sont rendues strictement vraies.

Référence : sections 8.1–8.6, 9.2 de l'analyse.

## TODOs

### objets de résultats publics (8.1)

- [ ] Remplacer les `dict[str, Any]` par des modèles stables : `ValidationReport`, `SemanticValidationReport`, `CompilationReport`, `CheckReport`, `Explanation`
- [ ] Chaque rapport doit hériter de `BaseModel` (Pydantic)
- [ ] Ajouter un test : l'API publique retourne des objets typés, pas des dicts

### ProjectContext / ProjectSession (8.2)

- [ ] Créer `ProjectSession` ou `ProjectContext` partagé entre `validate`, `validate_smt`, `compile`
- [ ] Éviter la reconstruction d'un `Compiler` à chaque méthode de `Project`
- [ ] Ajouter un cache de chargement dans la session
- [ ] Ajouter un test : deux appels à `project.validate()` puis `project.compile()` partagent le contexte

### injection réelle de LofSettings (8.3)

- [ ] Injecter `LofSettings` dans `Loader`, `Compiler`, `Solver`, `Graph`, `Pipeline`, `Writer`
- [ ] Supprimer les constructions directes (`LofSettings()`, `Compiler(self.root)`)
- [ ] Ajouter un test : modifier un paramètre dans LofSettings affecte le comportement du compilateur

### registre de profils (8.4)

- [ ] Créer un `ProfileRegistry` lisible depuis les fichiers de profil
- [ ] Remplacer la ligne codée en dur `fastapi-react` dans la CLI
- [ ] Ajouter un test : `lof profiles` liste les profils du registre

### suppression structure legacy (8.5)

- [ ] Décider du sort de `lof init` : migrer vers la nouvelle structure ou supprimer
- [ ] Si migration : aligner sur la structure README (`app/bronze`, `app/silver`, etc.)
- [ ] Si suppression : documenter la procédure de remplacement
- [ ] Supprimer les dossiers `definitions/types`, `templates/python`, `generated/python` si legacy

### vrai `lof diff` (3.6)

- [ ] Implémenter `lof diff` basé sur un `CompilationPlan` réel
- [ ] Calculer les hashes réels des artefacts rendus en mémoire
- [ ] Comparer avec le dernier manifeste
- [ ] Classer les artefacts : ajouté, modifié, supprimé, inchangé, impact indirect, modification manuelle
- [ ] Ajouter un test : modification Gold → seuls les artefacts concernés apparaissent comme modifiés

### compilation ciblée (instance, type)

- [ ] Implémenter `Compiler.compile(instance="...", type="...")`
- [ ] Ne compiler que les instances filtrées
- [ ] Ajouter un test : compilation ciblée par instance
- [ ] Ajouter un test : compilation ciblée par type

### manifestes déterministes

- [ ] Utiliser des identifiants déterministes (pas d'UUID) dans les manifestes
- [ ] Garantir que deux compilations identiques produisent le même manifeste
- [ ] Ajouter un test : `lof compile` deux fois de suite → mêmes hashes

### versionnement du DSL

- [ ] Ajouter un numéro de version au DSL Gold
- [ ] Ajouter un test de compatibilité ascendante
- [ ] Ajouter la version dans le manifeste

### gestion des exceptions (8.6)

- [ ] Remplacer les `except Exception` trop larges par des exceptions spécifiques
- [ ] `_resolve_output_path()` ne doit pas avaler silencieusement les erreurs de rendu
- [ ] Ajouter un test : output pattern invalide → échec avec diagnostic précis

### publication

- [ ] Ajouter un test d'installation du wheel : `pip install dist/*.whl` dans un environnement vierge
- [ ] Publier sur TestPyPI
- [ ] Ajouter une CI de publication conditionnelle

## Conversation

### user

Créer les tickets pour chaque phase de l'analyse détaillée du dépôt LOF-Framework.
