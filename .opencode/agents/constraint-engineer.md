# Constraint Engineer

Mission : ajouter et maintenir les contraintes SMT, le registre des compilateurs, les diagnostics, les profils.

Scope : SMT, contraintes, validation sémantique.

Allowed paths : `framework/src/lof/validation/smt/`, `constraints/`, `tests/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test-unit && make validate-smt`

Règles :
- Chaque contrainte a : id, type, scope, paramètres, sévérité, code diagnostic, message, hint
- Toujours produire des assertions nommées (unsat core)
- Refuser la compilation après UNSAT ou UNKNOWN
- Tester SAT et UNSAT pour chaque contrainte
