# Examples

## Minimal Example

The minimal example demonstrates the core concepts with:

- `named-element` - base type with a name
- `python-entity` - entity class generator
- `python-service` - service class generator  
- `markdown-document` - documentation generator
- `mermaid-node` - diagram generator

### Instances

- **Customer** - an entity with id, email, and name fields
- **Project** - an entity with id, title, and description fields
- **Customer Service** - a service for Customer entities
- **Project Service** - a service for Project entities
- **Model Diagram** - a Mermaid class diagram

### Patch

**customer-add-find-by-email**: Adds a static `find_by_email` method to `Customer`.
