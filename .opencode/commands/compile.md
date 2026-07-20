# /compile

Compile le projet LOF à partir des définitions, templates, instances et patches.

## Usage

```
/compile [--instance <id>] [--type <id>] [--dry-run]
```

## Comportement

1. Charge tous les types, instances, patches, cibles
2. Construit le graphe de dépendances
3. Valide l'intégrité
4. Résout les paramètres
5. Génère les artefacts via les templates
6. Applique les patches AST
7. Écrit les fichiers dans `generated/`
8. Met à jour le manifeste
