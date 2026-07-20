# /add-type

Ajoute un nouveau type au projet.

## Usage

```
/add-type <id> [--template <path>] [--target <target-id>]
```

## Comportement

1. Crée un fichier dans `definitions/types/<id>.json`
2. Ajoute les paramètres requis
3. Associe un template optionnel
4. Définit les dépendances
5. Valide le résultat
