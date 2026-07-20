# diagnostic-repair-loop

1. Lire le diagnostic → `.lof/diagnostics/latest.json`
2. Identifier la couche source → `repair-from-diagnostic`
3. Appliquer la correction minimale
4. Valider localement → `make test-unit`
5. Relancer SMT → `make validate-smt`
6. Compiler → `make compile`
7. Tester → `make test`
8. Arrêter après 3 tentatives max
