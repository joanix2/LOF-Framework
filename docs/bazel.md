# Bazel Integration

## Overview

The LOF framework uses Bazel for deterministic, hermetic builds.

## Rules

### lof_compile

The main build rule for compiling LOF projects:

```python
lof_compile(
    name = "generated_project",
    types = glob(["definitions/types/*.json"]),
    instances = glob(["instances/*.json"]),
    templates = glob(["templates/**/*"]),
    patches = glob(["patches/**/*.json"]),
    schemas = glob(["schemas/*.json"]),
    targets = glob(["definitions/targets/*.json"]),
)
```

## Targets

```bash
bazel build //:generated_project
bazel test //...
bazel run //tools:compile
```

## Constraints

- All inputs must be declared
- Outputs must be deterministic
- No network access during build
- No writes outside the Bazel sandbox
