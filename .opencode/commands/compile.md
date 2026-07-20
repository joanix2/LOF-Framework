# /compile

Compile uniquement après validation SMT réussie.

Usage : `/compile [--dry-run] [--instance <id>]`

Étapes : validate-model → templates → patches → generated project → linters.
