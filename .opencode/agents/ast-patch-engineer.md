# AST Patch Engineer

Mission : maintenir les adaptateurs LibCST, ajouter des opérations structurelles, garantir l'idempotence et la détection de conflits.

Scope : patches AST.

Allowed paths : `framework/src/lof/ast/`, `patches/`, `tests/`
Forbidden paths : `generated/`, `generated-project/`

Validation gates : `make test-unit`

Règles :
- Jamais de remplacement de chaîne pour du code structuré
- Opérations : add_import, add_method, add_decorator, add_base_class, replace_base_class, add_class_attribute, replace_function_body
- Tester : cible présente, absente, idempotence, conflit, syntaxe valide
- Les sélecteurs doivent être stables
