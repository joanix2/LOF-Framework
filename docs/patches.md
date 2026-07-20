# AST Patches

## Patch Definition

A patch describes structural AST transformations.

```json
{
  "id": "customer-add-find-by-email",
  "language": "python",
  "targetSelector": { "class": "Customer" },
  "operations": [
    {
      "op": "add_method",
      "name": "find_by_email",
      "parameters": [{ "name": "email", "annotation": "str" }],
      "returnType": "Optional[Customer]",
      "body": ["for item in self._items.values():", "    if item.email == email:", "        return item", "return None"]
    }
  ]
}
```

## Supported Operations (Python)

| Operation | Description |
|-----------|-------------|
| `add_import` | Add an import statement |
| `add_method` | Add a method to a class |
| `add_decorator` | Add a decorator to a class |
| `add_base_class` | Add a base class |
| `replace_base_class` | Replace all base classes |
| `add_class_attribute` | Add a class attribute |
| `replace_function_body` | Replace a function body |

## Patch Chaining

Patches are applied in order:

1. Order declared in the instance
2. Explicit patch dependencies
3. Ambiguity causes errors (no silent ordering)
