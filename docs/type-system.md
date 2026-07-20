# Type System

## Type Definition

A type describes a category of generated artifacts.

```json
{
  "id": "python-entity",
  "description": "Python class representing an entity",
  "dependsOn": ["named-element"],
  "parameters": {
    "name": { "type": "string", "required": true },
    "fields": { "type": "array", "required": true }
  },
  "template": "templates/python/entity.py.j2",
  "targetType": "python-module",
  "outputPattern": "generated/python/{{ name | snake_case }}.py"
}
```

## Parameters

Types declare parameters that instances must provide:

- `type`: the expected type (string, integer, array, etc.)
- `required`: whether the parameter must be provided
- `default`: fallback value if not provided
- `enum`: allowed values

## Dependencies

Types can depend on other types via `dependsOn`. This creates a directed acyclic graph (DAG) that determines compilation order.

## Targets

Each type can reference a target definition that specifies:

- Language
- File extension
- Formatter
- AST adapter
