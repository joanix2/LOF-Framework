# ticket-to-project

1. Créer ticket Bronze → `bronze-curator` / `add-bronze-ticket`
2. Extraire Silver → `semantic-extraction-engineer` / `extract-silver-claims`
3. Exécuter inférence → `reasoning-engineer` / `add-inference-rule`
4. Construire Gold → `gold-dsl-engineer` / `materialize-gold`
5. Valider SMT → `constraint-engineer` / `add-smt-constraint`
6. Compiler → `template-engineer` + `ast-patch-engineer`
7. Vérifier projet généré → `generated-project-validator` / `review-generated-project`
8. Tester → `test-engineer`
