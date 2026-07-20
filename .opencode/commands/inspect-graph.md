# /inspect-graph

Affiche le graphe de dépendances du projet.

## Usage

```
/inspect-graph [--format text|mermaid]
```

## Comportement

1. Charge tous les types et instances
2. Construit le graphe orienté
3. Détecte les cycles
4. Calcule l'ordre topologique
5. Affiche le résultat
