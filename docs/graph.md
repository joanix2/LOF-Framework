# Dependency Graph

## Two-Level Graph

### Declarative Graph

Describes the relationships between:

- Types and their dependencies
- Instances and their types
- Instances and patches

### Compilation Graph

Describes the transformation pipeline:

```
Instance
    ↓ template projection
Initial AST
    ↓ patch
Transformed AST
    ↓ formatting
Final file
```

## Cycle Detection

The graph validator detects cycles in type dependencies. Cycles produce explicit errors and block compilation.

## Topological Order

Types are compiled in dependency order. A type's dependencies are always compiled first.
