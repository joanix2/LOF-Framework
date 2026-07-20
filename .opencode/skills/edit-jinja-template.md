# edit-jinja-template

Objectif : modifier un template Jinja existant.

## Étapes

1. Identifier le type de projection associé au template
2. Examiner le contexte passé au template (vérifier `TemplateContextBuilder`)
3. Si la modification nécessite des données supplémentaires, les ajouter au contexte dans le `TemplateContextBuilder` ou le `GraphContextResolver`
4. Modifier le template
5. Vérifier les chemins de sortie (pas de path traversal)
6. Compiler l'exemple complet
7. Vérifier le projet généré
8. Mettre à jour les golden files si le changement est attendu
9. Tester : `make determinism-check && make compile && make test`
