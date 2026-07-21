# Formalisation M3 — méta-langage fondé sur la logique de réécriture

```
L = (Σ, E, C, I, R)

Σ : signature, types et constructeurs
E : équations et fonctions déterministes
C : contraintes de validité
I : règles d'inférence
R : règles de réécriture
```

## Niveaux

| Niveau | Rôle | Technologie |
|--------|------|-------------|
| **M3** | Méta-langage : définit ce qu'est un langage génératif | Python + JSON Schema |
| **M2** | DSL de modélisation d'applications : Model, Attribute, Relation, Role, Permission | `profiles/fastapi-react/profile.json` |
| **M1** | Programme ISOCLIM écrit dans le DSL | `isoclim.json` |
| **M0** | Application concrète générée et exécutée | FastAPI + React + données |

## Pipeline

```
M1 brut
    ↓ validation (contraintes C)
M1 valide
    ↓ inférence (règles I)
M1 normalisé et enrichi
    ↓ réécriture (règles R)
IR backend + IR frontend
    ↓ rendu (templates Jinja)
M0 FastAPI + React
```

## Distinction inférence / réécriture

- **Inférence** : ajoute une connaissance implicite au modèle (même espace sémantique)
- **Réécriture** : transforme le modèle vers une autre représentation (espace technique)

## Structure M3 minimale

```json
{
  "types": ["Application", "Model", "Attribute", "Relation", "Artifact"],
  "constructors": [
    {"name": "model", "arguments": ["Identifier", "List<Attribute>", "List<Relation>"], "returns": "Model"}
  ],
  "functions": [
    {"name": "defaultWidget", "arguments": ["DataType"], "returns": "WidgetType"}
  ],
  "constraints": [
    {"name": "relationTargetExists", "scope": "Application"}
  ],
  "inferenceRules": [
    {"name": "addImplicitId", "input": "ModelWithoutPrimaryKey", "output": "ModelWithUUIDPrimaryKey"}
  ],
  "rewriteRules": [
    {"name": "modelToCrudArtifacts", "input": "Model", "output": "ArtifactSet"}
  ]
}
```
