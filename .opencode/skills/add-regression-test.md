# add-regression-test

Objectif : ajouter un test de non-régression pour un bug corrigé.

## Étapes

1. Réduire le bug à un exemple minimal reproductible
2. Choisir le niveau approprié (unitaire, intégration, benchmark)
3. Écrire un test qui échoue (qui reproduit le bug)
4. Vérifier que le test échoue pour la bonne raison
5. Appliquer la correction
6. Vérifier que le test passe
7. Vérifier les tests voisins (pas de régression)
8. Ajouter un scénario de benchmark si le bug est transversal
