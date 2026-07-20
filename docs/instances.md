# Instances

## Instance Definition

An instance is a concrete use of a type with specific parameter values.

```json
{
  "id": "customer",
  "type": "python-entity",
  "values": {
    "name": "Customer",
    "fields": [
      { "name": "id", "type": "UUID" },
      { "name": "email", "type": "str" }
    ]
  },
  "patches": ["customer-add-find-by-email"]
}
```

## Resolution Rules

Parameter values are resolved in this priority order:

1. Inherited values (from dependency types)
2. Default values from the current type
3. Instance values (highest priority)

## Patches

Instances can reference patches for local AST transformations. Patches are applied after template rendering.
