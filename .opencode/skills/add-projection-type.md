# add-projection-type

Objectif : ajouter un nouveau type de projection (un nouveau type de fichier généré).

## Étapes

1. Créer la définition du type dans `definitions/types/`
2. Créer le template Jinja associé dans `templates/`
3. Déclarer le paramétrage et le contexte attendu
4. Ajouter la cible dans `definitions/targets/` si nécessaire
5. Créer une instance de test
6. Compiler et vérifier le fichier généré
7. Ajouter un golden test
8. Tester : `make test-generation && make determinism-check`
