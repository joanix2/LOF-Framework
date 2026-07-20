# Claude Code — Instructions

Tu travailles sur le LOP Framework : une chaîne de compilation neuro-symbolique qui transforme des expressions utilisateur en applications FastAPI + React générées.

## Pipeline

```
Bronze → Silver → Reasoning → Gold → SMT → Compilation → Projet validé
```

## Pour répondre à une question sur le code

1. Consulte `graphify-out/GRAPH_REPORT.md` pour une vue d'ensemble
2. Utilise `graphify query "<question>"` pour naviguer dans le graphe de connaissances
3. Utilise `graphify path <A> <B>` pour tracer les connexions entre concepts
4. Utilise `graphify explain <concept>` pour analyser un nœud

## Pour modifier le projet

1. Identifie la couche concernée (types/instances/templates/patches/règles)
2. Vérifie les duplications dans `domain/` et `infrastructure/`
3. Localise les tests dans `framework/tests/`
4. Écris d'abord un test, puis modifie le code
5. Exécute `make format && make lint && make typecheck && make test` après chaque changement

## Interdictions

- Ne jamais modifier `generated/` ou `generated-project/` directement
- Ne jamais contourner la validation SMT (Z3)
- Ne jamais placer de logique métier dans Jinja
- Ne jamais écraser les données Bronze (append-only)
