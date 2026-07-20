# Politique des fichiers générés

## Interdiction stricte

Ne jamais modifier directement :

- `generated/`
- `generated-project/`
- `packages/api-client/src/generated/`
- `graphify-out/`

Ces répertoires sont produits par la compilation et seront écrasés.

## Source de vérité

La source de vérité est constituée de :

- `definitions/types/` — définitions de types
- `instances/` — instances d'entités
- `templates/` — templates Jinja
- `patches/` — patches AST
- `schemas/` — schémas JSON
- `rules/` — règles d'inférence
- `constraints/` — contraintes SMT

## En cas d'erreur dans un fichier généré

1. Identifier le type, le template ou le patch qui a produit ce fichier
2. Corriger la source déclarative
3. Recompiler
4. Vérifier que le correctif est appliqué

Ne jamais patcher le fichier généré directement.
