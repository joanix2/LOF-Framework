# /add-patch

Ajoute un patch AST pour une instance.

## Usage

```
/add-patch <id> --instance <instance-id> --language <lang>
```

## Comportement

1. Inspecte l'AST cible
2. Crée un patch structurel (pas de remplacement textuel)
3. Teste le patch
4. Relance la compilation
