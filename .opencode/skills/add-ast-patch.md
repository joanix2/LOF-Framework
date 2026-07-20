# add-ast-patch

Objectif : ajouter un patch AST structurel.

## Étapes

1. Vérifier qu'un patch est préférable à un paramètre Gold ou à une modification de template
2. Identifier le langage (Python → LibCST, TypeScript → ts-morph)
3. Définir un sélecteur stable (classe, fonction)
4. Implémenter l'opération structurelle dans `patches/`
5. Ajouter les diagnostics
6. Tester l'application sur une cible existante
7. Tester l'idempotence (appliquer deux fois)
8. Tester la cible absente
9. Tester les conflits avec d'autres patches
10. Compiler et valider l'exemple : `make compile && make test`
