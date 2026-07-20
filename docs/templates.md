# Templates

## Jinja Templates

Templates use Jinja2 with custom filters.

## Built-in Filters

| Filter | Description | Example |
|--------|-------------|---------|
| `snake_case` | Convert to snake_case | `HelloWorld` → `hello_world` |
| `camel_case` | Convert to camelCase | `hello_world` → `helloWorld` |
| `pascal_case` | Convert to PascalCase | `hello_world` → `HelloWorld` |
| `kebab_case` | Convert to kebab-case | `hello_world` → `hello-world` |
| `pluralize` | Pluralize a word | `cat` → `cats` |

## Best Practices

- Keep templates simple
- Avoid complex business logic in templates
- Use filters for name transformations
- Let patches handle local variations
