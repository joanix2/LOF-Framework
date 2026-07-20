# Language-Oriented Programming Framework

A framework for **Language-Oriented Programming** that generates deterministic code from type definitions, Jinja templates, instances, and AST patches.

## Concept

```
types + templates + instances + patches
→ deterministic code generation
```

## Quick Start

```bash
pip install -e .
lof init
lof validate
lof compile
lof graph
```

## Project Structure

- `definitions/types/` - Type definitions
- `templates/` - Jinja templates
- `instances/` - Instance definitions
- `patches/` - AST patches
- `generated/` - Generated output (never edit directly)
- `schemas/` - JSON Schema files

## Documentation

See `docs/` for detailed documentation.

## License

MIT
