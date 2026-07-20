# add-bronze-ticket

Objectif : ajouter un ticket Bronze append-only.

## Étapes

1. Exécuter `lof bronze add "<texte>" --source <source> --type <type>`
2. Vérifier que le ticket est créé dans `data/bronze/entries/`
3. Vérifier que les entités et claims Silver sont extraits (`lof silver status`)
4. Vérifier la provenance Bronze → Silver
