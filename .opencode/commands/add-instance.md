# /add-instance

Ajoute une nouvelle instance d'un type existant.

## Usage

```
/add-instance <id> --type <type-id>
```

## Comportement

1. Lit les types existants
2. Identifie les paramètres requis du type
3. Crée le fichier d'instance dans `instances/<id>.json`
4. Valide
5. Compile
6. Affiche les fichiers générés
