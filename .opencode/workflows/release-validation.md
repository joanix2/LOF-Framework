# release-validation

1. Lancer la CI complète → `make ci`
2. Exécuter le benchmark → `make benchmark-smoke`
3. Tester le projet généré → `review-generated-project`
4. Mettre à jour `CHANGELOG.md`
5. Mettre à jour la version dans `pyproject.toml`
6. Vérifier les migrations
7. Créer le tag et la release
