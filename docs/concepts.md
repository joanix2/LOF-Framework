# Language-Oriented Programming: Concepts

## Paradigm Overview

Language-Oriented Programming (LOP) shifts the source of truth from code to **language definitions**.

Instead of writing code directly, you define:

- **Types** - the structure of your domain
- **Templates** - how types are projected into code
- **Instances** - concrete values for types
- **Patches** - AST transformations for local variations

## Core Principle

```
types + templates + instances + patches
→ deterministic code generation
```

## Source of Truth

**Never modify generated code directly.**

The source of truth is:

```
definitions/types/   → type definitions
templates/           → Jinja templates
instances/           → instance definitions
patches/             → AST patches
```

## Pipeline

1. **Load** types, instances, patches, and targets
2. **Build** the dependency graph
3. **Validate** constraints and detect cycles
4. **Resolve** parameters (inherited values → defaults → instance values)
5. **Render** templates with resolved context
6. **Patch** AST with structural transformations
7. **Format** and write generated files
8. **Manifest** the build result
