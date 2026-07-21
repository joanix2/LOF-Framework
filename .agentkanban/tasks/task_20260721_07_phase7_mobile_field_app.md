---
title: "Phase 7 — Génération d'application mobile terrain (ISOCLIM)"
lane: todo
created: 2026-07-21T00:00:00Z
updated: 2026-07-21T00:00:00Z
description: >
  Créer un profil LOF pour générer une application mobile terrain destinée
  aux techniciens sur chantier. Stack cible : React Native + Expo (ou équivalent
  mobile-first). L'application permet de consulter le planning, gérer les
  missions (démarrage, pause, fin), ajouter commentaires/photos,
  signaler des problèmes, signer les comptes rendus.
  Données démo : entreprise ISOCLIM JG, équipe de 3 personnes, 8 missions.
---

## Contexte

Demande : générer une application mobile terrain complète, pas une démo à
boutons vides. L'utilisateur terrain doit pouvoir réellement :
- consulter son planning (aujourd'hui/semaine)
- voir le détail de ses missions (client, adresse, contact, description)
- cocher des checklists (sécurité, matériel, matériaux)
- démarrer / mettre en pause / reprendre / terminer une mission
- ajouter des commentaires (texte libre + rapides prédéfinis)
- ajouter des photos (catégories avant/pendant/après)
- signaler un problème (type, gravité, description, photo, bloquant/non)
- remplir un compte rendu de fin de mission
- signer (simulé) pour validation client
- consulter l'historique chronologique de la mission
- voir son profil (équipe, habilitations, véhicule)
- recevoir des notifications terrain

Stack cible : React Native + Expo Router + AsyncStorage (stockage local).
Pas d'authentification complexe — l'app s'ouvre directement sur le profil
de Julien Moreau (mode démo).

Référence : prompt ISOCLIM Terrain complet (sections 1–19).

## TODOs

### Profil LOF : `mobile-field`

- [ ] Créer `profiles/mobile-field/` avec : `profile.yaml`, règles d'inférence, templates, types, instances de démo
- [ ] Définir dans `profile.yaml` : langage cible (`typescript`), framework (`react-native`, `expo`), validateurs (`tsc`, `eslint`, `jest`)
- [ ] Enregistrer le profil dans `ProfileRegistry` (Phase 6)
- [ ] Ajouter le profil dans la CLI (`lof new --profile mobile-field`)
- [ ] Ajouter un test : `lof new demo --profile mobile-field` crée la structure correcte

### Types LOF pour mobile-field

- [ ] Créer `definitions/types/mobile/screen_mission_list.json` — type pour l'écran liste de missions
- [ ] Créer `definitions/types/mobile/screen_mission_detail.json` — type pour l'écran détail mission
- [ ] Créer `definitions/types/mobile/screen_today.json` — type pour l'écran aujourd'hui
- [ ] Créer `definitions/types/mobile/screen_planning.json` — type pour l'écran planning
- [ ] Créer `definitions/types/mobile/screen_profile.json` — type pour l'écran profil
- [ ] Créer `definitions/types/mobile/mission_card.json` — type pour carte mission (réutilisable)
- [ ] Créer `definitions/types/mobile/employee_profile.json` — type pour profil employé
- [ ] Créer `definitions/types/mobile/comment.json` — type pour commentaire
- [ ] Créer `definitions/types/mobile/photo.json` — type pour photo
- [ ] Créer `definitions/types/mobile/problem_report.json` — type pour signalement
- [ ] Créer `definitions/types/mobile/checklist_item.json` — type pour item de checklist
- [ ] Créer `definitions/types/mobile/mission_log_entry.json` — type pour entrée d'historique
- [ ] Créer `definitions/types/mobile/notification.json` — type pour notification

### Targets LOF pour mobile-field

- [ ] Créer `definitions/targets/expo_component.json` — cible pour composant Expo (`.tsx`)
- [ ] Créer `definitions/targets/expo_screen.json` — cible pour écran Expo (`.tsx` + route)
- [ ] Créer `definitions/targets/expo_service.json` — cible pour service/data layer (`.ts`)
- [ ] Créer `definitions/targets/expo_config.json` — cible pour fichier de config (`.json`, `.ts`)

### Règles d'inférence : profil mobile-field

- [ ] Créer `src/lof/reasoning/profiles/mobile_field.py` avec les règles de projection mobile :
  - `entity → mission_screen` (un écran par type d'entité mission)
  - `operation → service_method` (CRUD → services API)
  - `checklist → checklist_component`
  - `problem_type → report_form_component`
  - `employee → profile_screen`
- [ ] Définir les prédicats du domaine terrain : `mission`, `employee`, `client`, `worksite`, `checklist`, `material`, `problem_type`, `comment`, `photo`
- [ ] Ajouter un test : le profil `mobile-field` produit des projections valides

### Instances de démonstration (ISOCLIM)

- [ ] Créer `instances/mobile/employee_julien.json` — Julien Moreau, chef d'équipe
- [ ] Créer `instances/mobile/employee_karim.json` — Karim Benali, poseur
- [ ] Créer `instances/mobile/employee_lucas.json` — Lucas Martin, technicien
- [ ] Créer `instances/mobile/client_atlantique.json` — Atlantique Surgelés
- [ ] Créer `instances/mobile/client_boulangerie.json` — Boulangerie Océane
- [ ] Créer `instances/mobile/client_logistique.json` — Logistique Charentaise
- [ ] Créer `instances/mobile/client_boucherie.json` — Boucherie du Centre
- [ ] Créer `instances/mobile/client_poissons.json` — Poissons de l'Atlantique
- [ ] Créer `instances/mobile/worksite_extension_chambre.json` — Extension chambre froide négative
- [ ] Créer `instances/mobile/worksite_extension_stockage.json` — Extension zone de stockage
- [ ] Créer `instances/mobile/worksite_zone_industrielle.json` — Zone industrielle Pons
- [ ] Créer `instances/mobile/worksite_boucherie.json` — Boucherie du Centre Jonzac
- [ ] Créer `instances/mobile/worksite_nouvelle_zone_froide.json` — Nouvelle zone froide
- [ ] Créer 8 missions (cf cas 1–5 + 3 supplémentaires) avec statuts variés :
  - `mission_panneaux_atlantique.json` — Planifiée (cas 1)
  - `mission_porte_boulangerie.json` — En cours (cas 2, avec problème)
  - `mission_maintenance_logistique.json` — Terminée (cas 3)
  - `mission_depannage_boucherie.json` — Urgente (cas 4)
  - `mission_reception_poissons.json` — Planifiée (cas 5)
  - `mission_controle_qualite.json` — En cours
  - `mission_installation_rapide.json` — Planifiée
  - `mission_sav_client.json` — Terminée
- [ ] Créer 15 commentaires, 12 photos fictives, 3 signalements
- [ ] Créer l'équipe "Équipe Pose 2" avec les 3 employés et le véhicule Renault Master GH-482-KL
- [ ] Ajouter les habilitations : Travail en hauteur, CACES nacelle, Habilitation électrique, Permis B

### Templates React Native / Expo

- [ ] Créer `templates/mobile/` avec tous les templates `.tsx.j2` et `.ts.j2`

#### Templates : Layout et navigation

- [ ] `templates/mobile/layout/app.tsx.j2` — Root component avec Expo Router
- [ ] `templates/mobile/layout/_layout.tsx.j2` — Bottom tab navigation (4 onglets : Aujourd'hui, Planning, Missions, Profil)
- [ ] `templates/mobile/layout/mission_layout.tsx.j2` — Layout pour le flux mission (avec chronomètre en haut)

#### Templates : Écran Aujourd'hui

- [ ] `templates/mobile/screens/today.tsx.j2` — Écran d'accueil :
  - En-tête "Bonjour Julien", date, équipe, véhicule
  - Carte mission principale (heure, nom, client, chantier, adresse, distance, durée, statut, priorité)
  - Boutons : Voir la mission, Itinéraire, Appeler, Démarrer
  - Autres missions du jour (petites cartes)

#### Templates : Écran Planning

- [ ] `templates/mobile/screens/planning.tsx.j2` — Planning avec vues Aujourd'hui / Semaine
  - Cartes mission avec date, horaire, client, chantier, type, statut, adresse, équipe
  - Badges de statut (Planifiée/En route/En cours/En pause/Bloquée/Terminée)
  - Consultation uniquement (pas d'édition)

#### Templates : Écran Liste Missions

- [ ] `templates/mobile/screens/mission_list.tsx.j2` — Liste avec 3 sections :
  - À venir, En cours, Terminées
  - Recherche par client/chantier/adresse/référence
  - Cartes avec titre, date, statut, client, adresse, durée

#### Templates : Écran Détail Mission

- [ ] `templates/mobile/screens/mission_detail.tsx.j2` — Écran principal de mission :
  - En-tête : référence, titre, statut, priorité, horaire, durée
  - Bloc chantier : client, adresse, contact, téléphone, horaires accès
  - Boutons : Itinéraire, Appeler, Message
  - Bloc description
  - Bloc consignes de sécurité (checklist cochable)
  - Bloc équipe (chef + membres + téléphones + véhicule)
  - Bloc matériel nécessaire (checklist : Présent/Manquant/Endommagé)
  - Bloc matériaux nécessaires (checklist : Chargé/Livré/Manquant)

#### Templates : Chronomètre et actions mission

- [ ] `templates/mobile/components/mission_timer.tsx.j2` — Chronomètre avec :
  - Durée écoulée affichée
  - Bouton Pause (avec sélection de raison : repas, attente matériel, client, technique, intempéries)
  - Bouton Reprendre
  - Durée de pause enregistrée

#### Templates : Commentaires

- [ ] `templates/mobile/components/comment_section.tsx.j2` — Section commentaires :
  - Liste : auteur, heure, texte, photos jointes
  - Champ texte libre
  - Commentaires rapides prédéfinis (travail commencé, matériel reçu, matériel manquant, accès impossible, attente client, problème technique, travaux terminés)

#### Templates : Photos

- [ ] `templates/mobile/components/photo_section.tsx.j2` — Section photos :
  - Bouton appareil photo / galerie
  - Catégories : Avant / Pendant / Après intervention
  - Chaque photo : date, heure, auteur, commentaire facultatif
  - Images fictives en mode démo

#### Templates : Signalement de problème

- [ ] `templates/mobile/components/problem_report.tsx.j2` — Formulaire signalement :
  - Type (dropdown : matériel manquant, endommagé, mauvaise livraison, accès impossible, sécurité, technique, plan incorrect, demande client, retard, autre)
  - Gravité (Mineur / Important / Bloquant)
  - Description (texte)
  - Photo facultative
  - Checkbox "Mission bloquée"
  - Si bloquant → statut "Bloquée", alerte visible

#### Templates : Fin de mission

- [ ] `templates/mobile/screens/mission_completion.tsx.j2` — Écran de fin :
  - Résumé automatique : heure prévue, réelle début/fin, durée totale, pause, travail réel, photos, commentaires, problèmes
  - Checklist de clôture : zone nettoyée, matériel récupéré, installation vérifiée, photos finales, client informé, réserves enregistrées
  - Champ compte rendu texte
  - Statut final : Terminée / Terminée avec réserves / À poursuivre / Bloquée
  - Validation client : nom, signature simulée, ou "Client non disponible"

#### Templates : Historique

- [ ] `templates/mobile/components/mission_timeline.tsx.j2` — Timeline chronologique :
  - Entrées : heure + action (arrivée, démarrée, photo, problème, pause, reprise, compte rendu, terminée)
  - Icônes par type d'événement

#### Templates : Écran Profil

- [ ] `templates/mobile/screens/profile.tsx.j2` — Profil employé :
  - Prénom, nom, poste, équipe, téléphone, véhicule
  - Compétences et habilitations (avec alerte expiration proche)
  - Statistiques : missions terminées cette semaine

#### Templates : Notifications

- [ ] `templates/mobile/components/notification_list.tsx.j2` — Liste de notifications terrain :
  - Mission modifiée, nouvelle mission, horaire changé, matériel disponible, problème traité, commentaire responsable, mission annulée
  - Exemples concrets intégrés dans les données démo

#### Templates : Data Layer

- [ ] `templates/mobile/services/storage.ts.j2` — Service AsyncStorage :
  - CRUD pour missions, employés, commentaires, photos
  - Mode démo avec données préchargées
- [ ] `templates/mobile/services/mission_service.ts.j2` — Logique métier mission :
  - démarrer, pause, reprendre, terminer
  - Validation des checklists
  - Calcul durées
- [ ] `templates/mobile/hooks/useMissionTimer.ts.j2` — Hook chronomètre
- [ ] `templates/mobile/hooks/useMissions.ts.j2` — Hook liste/recherche missions
- [ ] `templates/mobile/types/index.ts.j2` — Types TypeScript partagés

### Templates : Configuration du projet

- [ ] `templates/mobile/config/app.json.j2` — Expo config (nom, slug, icon, splash)
- [ ] `templates/mobile/config/package.json.j2` — Dépendances : expo, react-native, expo-router, expo-camera, expo-image-picker, async-storage
- [ ] `templates/mobile/config/tsconfig.json.j2` — TypeScript config
- [ ] `templates/mobile/config/babel.config.js.j2` — Babel config Expo
- [ ] `templates/mobile/config/.gitignore.j2` — Ignores mobile (node_modules, .expo, dist)

### Compilation et intégration

- [ ] Vérifier que `lof compile --profile mobile-field` génère l'arborescence correcte
- [ ] Vérifier que `generated/` contient :
  ```
  apps/mobile/
  ├── app/
  │   ├── _layout.tsx
  │   ├── (tabs)/
  │   │   ├── _layout.tsx
  │   │   ├── today.tsx
  │   │   ├── planning.tsx
  │   │   ├── missions.tsx
  │   │   └── profile.tsx
  │   └── mission/
  │       ├── [id].tsx
  │       └── completion.tsx
  ├── components/
  │   ├── MissionCard.tsx
  │   ├── MissionTimer.tsx
  │   ├── CommentSection.tsx
  │   ├── PhotoSection.tsx
  │   ├── ProblemReport.tsx
  │   ├── MissionTimeline.tsx
  │   ├── ChecklistSection.tsx
  │   ├── StatusBadge.tsx
  │   └── NotificationList.tsx
  ├── services/
  │   ├── storage.ts
  │   └── mission_service.ts
  ├── hooks/
  │   ├── useMissionTimer.ts
  │   └── useMissions.ts
  ├── types/
  │   └── index.ts
  ├── data/
  │   └── demo.ts
  ├── app.json
  ├── package.json
  ├── tsconfig.json
  ├── babel.config.js
  └── .gitignore
  ```
- [ ] Ajouter un test : la génération mobile-field produit des fichiers `.tsx` et `.ts` valides
- [ ] Ajouter un test : `npx expo export --platform web` réussit sur le projet généré
- [ ] Ajouter un test : les données démo sont cohérentes (8 missions, 3 employés, liens valides)

### CI pour mobile-field

- [ ] Ajouter un job `generated-mobile` dans `.github/workflows/` :
  - `lof compile --profile mobile-field`
  - `cd generated/apps/mobile && npm install`
  - `npx tsc --noEmit` (typecheck)
  - `npx expo export --platform web` (build)
- [ ] Ajouter un test de non-régression : même compilation → mêmes hashes (cf Phase 2)

## Conversation

### user

phase 7 le framework dois pouvoir générer le prototype mobile terrain ISOCLIM décrit dans le prompt.
