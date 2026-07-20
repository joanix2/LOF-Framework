# Règles de programmation orientée langage

## Source de vérité

Le code généré n'est jamais la source de vérité.

La source de vérité est constituée de :

- `definitions/types/`
- `templates/`
- `instances/`
- `patches/`

## Modifications métier

Pour modifier un élément spécifique du projet :

1. modifier une instance ;
2. ajouter un patch AST si la variation est locale ;
3. lancer `make compile` ;
4. lancer `make check`.

## Modifications globales

Pour modifier tous les artefacts d'un type :

1. modifier le type ou son template ;
2. relancer la compilation ;
3. vérifier toutes les sorties impactées.

## Code généré

Ne jamais modifier directement `generated/`.

Toute modification directe sera écrasée ou détectée comme divergence.

## Patches

Utiliser un patch AST pour une variation locale.

Si plusieurs instances utilisent le même patch, envisager de créer un type plus spécialisé ou de modifier le template.

## Interfaces statiques

Les fichiers de `interfaces/` peuvent être copiés comme artefacts standards.

## Validation obligatoire

Après toute modification :

```bash
make validate
make compile
make check
make test
```
