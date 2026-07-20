# LLM Workflow

## How LLMs Should Use This Framework

### Do

- Modify type definitions in `definitions/types/`
- Modify or create templates in `templates/`
- Modify or create instances in `instances/`
- Create AST patches in `patches/` for local variations
- Run `make compile` after changes
- Run `make check` to validate

### Don't

- Modify files in `generated/` - they will be overwritten
- Use string replacement for code changes - use AST patches
- Add business logic to templates - use patches instead

## Workflow

1. Define or modify types
2. Create or update templates
3. Add instances with parameter values
4. Apply AST patches for local variations
5. Run `make compile`
6. Run `make validate && make check && make test`
