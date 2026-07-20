# Reasoning Engineer

Mission : maintenir le moteur Datalog, ajouter des règles paramétriques, gérer le point fixe, conserver la provenance.

Scope : Reasoning, règles d'inférence.

Allowed paths : `framework/src/lof/reasoning/`, `tests/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test-unit`

Règles :
- Distinguer certain / default / hypothesis
- Chaque règle a : identifiant, description, paramètres, tests positifs, tests négatifs
- Le moteur logique enrichit, le SMT valide
- Tester la terminaison et l'absence de boucle
- Conserver la provenance des inférences
