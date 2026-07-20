# Validation Gates

## Gate locale (changement isolé)

```bash
make format && make lint && make typecheck && make test-unit
```

## Gate couche

```bash
make test               # tous les tests
make benchmark-smoke    # benchmark + compilation
```

## Gate pipeline

```bash
make validate           # validation structurelle
make validate-smt       # validation sémantique SMT
make compile            # compilation complète
make determinism-check  # vérification de déterminisme
```

## Gate complète

```bash
make ci
```

Chaque agent doit exécuter les gates appropriées après modification et indiquer lesquelles ont été passées.
