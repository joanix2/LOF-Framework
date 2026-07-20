# inspect-instance-graph

Objectif : inspecter le graphe des instances et leurs relations.

## Étapes

1. Exécuter `lof graph` pour le graphe des types
2. Utiliser `lof inspect instance --id <id>` pour une instance spécifique
3. Vérifier les relations déclarées dans les instances
4. Vérifier les dépendances transitives via `graphify path <A> <B>`
5. Vérifier l'absence de cycles dans les relations
