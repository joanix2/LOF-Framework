# Compilation

## Pipeline Steps

1. **Loading**: Load all types, instances, patches, and targets from JSON files
2. **Graph Construction**: Build the dependency graph using NetworkX
3. **Validation**: 
   - Schema validation against JSON Schema
   - Semantic validation (missing types, duplicate IDs)
   - Graph validation (cycles, missing dependencies)
4. **Parameter Resolution**: Merge inherited values, defaults, and instance values
5. **Template Rendering**: Project each instance through its type's template
6. **AST Patching**: Apply structural transformations
7. **Writing**: Write files to the output directory
8. **Manifest**: Update the build manifest

## Commands

```bash
# Full compilation
lof compile

# Dry run (show what would be generated)
lof compile --dry-run

# Compile specific instance
lof compile --instance customer

# Compile all instances of a type
lof compile --type python-entity
```
