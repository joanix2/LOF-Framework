# trace-pipeline-impact

Objectif : déterminer les effets d'un changement sur toute la chaîne.

## Étapes

1. Identifier la fonctionnalité ou le fichier modifié
2. Pour chaque couche, déterminer l'impact : Bronze / Silver / Reasoning / Gold / SMT / Graph / Templates / Patches / Generated project / Tests
3. Produire une matrice d'impact

Exemple :
```
Ajout d'un type de champ `money`
Bronze: aucun impact
Silver: extraction lexicale éventuelle
Reasoning: aucune règle obligatoire
Gold: nouveau type de champ
SMT: compatibilité des valeurs par défaut
Templates: SQLAlchemy, Pydantic, Zod, React
Tests: propagation multi-cible
```
