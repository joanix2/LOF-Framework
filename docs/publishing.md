# Publication PyPI

## Build

```bash
uv build
```

Produit dans `dist/` :

```
lof_framework-0.2.0-py3-none-any.whl
lof_framework-0.2.0.tar.gz
```

## Test local

```bash
uv tool install dist/lof_framework-0.2.0-py3-none-any.whl
lof --version
lof --help
```

## TestPyPI

```bash
uv publish --publish-url https://test.pypi.org/legacy/
uv tool install --index https://test.pypi.org/simple/ lof-framework
```

## PyPI (production)

La publication est automatisée par GitHub Actions lors de la création d'une release.

### Créer une release

```bash
# Mettre à jour la version dans pyproject.toml et CHANGELOG.md
git tag v0.2.0
git push origin v0.2.0
gh release create v0.2.0 --title "v0.2.0" --notes "See CHANGELOG.md"
```

Le workflow `.github/workflows/publish.yml` construit le package et le publie sur PyPI via Trusted Publishing.

### Trusted Publishing

Le dépôt GitHub doit être configuré sur PyPI :

1. Aller sur https://pypi.org/manage/account/publishing/
2. Ajouter un nouveau pending publisher
3. PyPI Project: `lof-framework`
4. GitHub Owner: `graphify-labs`
5. GitHub Repository: `lof`
6. Workflow name: `publish.yml`
7. Environment: `pypi`

## URLs

| Registre | URL |
|----------|-----|
| PyPI | https://pypi.org/project/lof-framework/ |
| TestPyPI | https://test.pypi.org/project/lof-framework/ |
| GitHub | https://github.com/graphify-labs/lof |

## Installation

```bash
# Production (PyPI)
uv tool install lof-framework

# Dernière version (GitHub)
uv tool install git+https://github.com/graphify-labs/lof.git

# Exécution ponctuelle
uvx lof-framework new demo --profile fastapi-react

# Depuis les sources
git clone https://github.com/graphify-labs/lof.git
cd lof
uv tool install .
```
