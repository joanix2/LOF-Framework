# repair-from-diagnostic

Objectif : corriger le modèle à partir d'un diagnostic structuré.

Entrée : diagnostic JSON (`.lof/diagnostics/latest.json`)

## Étapes

1. Lire le code du diagnostic
2. Lire les chemins JSON sources
3. Identifier la couche source (Gold / type / template / patch / règle / contrainte)
4. Identifier la correction minimale (ne pas modifier plus que nécessaire)
5. Modifier uniquement la source déclarative adaptée
6. Relancer la validation la plus locale (`make test-unit`)
7. Relancer SMT si nécessaire (`make validate-smt`)
8. Compiler uniquement après SAT (`make compile`)
9. Lancer les tests impactés
10. Arrêter après 3 tentatives max (pas de boucle infinie)

Ordre de correction : ticket → règle Silver → règle d'inférence → Gold → contrainte → type → template → patch
