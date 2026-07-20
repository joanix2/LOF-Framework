# Règles de code

## Structure

- Une fonction = une responsabilité
- Une classe = une raison de changer
- Éviter les fichiers > 350 lignes
- Éviter les fonctions > 50 lignes
- Éviter plus de 3 niveaux d'imbrication
- Pas de classes nommées `Manager`, `Utils`, `Helpers`

## Typage

- Toutes les signatures publiques sont typées
- Utiliser Pydantic v2 pour les DTO et configurations
- Utiliser `dataclass(frozen=True)` pour les objets de domaine
- Utiliser `Protocol` pour les ports
- Utiliser `Enum` / `Literal` pour les ensembles fermés
- Éviter `dict[str, Any]` quand un modèle structuré existe
- Pas de `type: ignore` sans commentaire justifiant pourquoi

## Configuration

- Pas de valeurs métier en dur — utiliser `domain/settings.py`
- Pas de chemins en dur — utiliser les settings
- Pas de noms de solveurs, timeout, profondeurs en dur

## Dépendances

- Le domaine (`domain/`) ne dépend pas de l'infrastructure
- Les dépendances externes (spaCy, Z3, NetworkX, Jinja) sont isolées derrière des ports
- Les adaptateurs concrets sont dans `infrastructure/adapters/`
