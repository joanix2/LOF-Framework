# Architecture MDE à 4 niveaux

```
M3  Métacompilateur    src/lof/                        Python
     ↓ instanceOf
M2  Métamodèle (DSL)   GoldApplication, GoldEntity,     Pydantic / JSON Schema
                       GoldField, GoldRelation…
     ↓ instanceOf  
M1  Modèle (programme) isoclim.json, library.json       JSON
     ↓ instanceOf
M0  Système concret    generated-project/apps/…         FastAPI + React
```

## Les niveaux

| Niveau | Rôle | Technologie | Emplacement |
|--------|------|-------------|-------------|
| **M3** | Métacompilateur | Python (Pydantic, Jinja, Z3, NetworkX) | `src/lof/` |
| **M2** | Métamodèle du DSL | `GoldApplication`, `GoldEntity`, `GoldField`, `GoldRelation`… | `src/lof/models/gold_models.py` + `schemas/gold-application.schema.json` |
| **M1** | Programme dans le DSL | JSON validé par le schéma M2 | `tests/fixtures/json/isoclim.json` |
| **M0** | Application générée | FastAPI + React (autonome, sans LOF) | `isoclim/generated-project/` |

## Relations

- **M3 → M2** : Le métacompilateur définit le langage (les `Gold*` models Pydantic sont le métamodèle)
- **M2 → M1** : Le programme JSON est une instance du métamodèle (validé par Pydantic)
- **M1 → M0** : Le compilateur transforme le programme en code exécutable via Jinja + patches AST

## Principe

Le métacompilateur (M3) ne connaît pas le programme (M1). Il ne connaît que le langage (M2).

Le programme (M1) ne contient que des décisions métier. Il ignore comment le compilateur fonctionne.

L'application générée (M0) ne dépend pas du métacompilateur (M3). Elle est autonome.

## Concrètement

```python
# M3 → src/lof/gold/json_loader.py
def load_gold_application(path: str | Path) -> GoldApplication:
    data = json.loads(path.read_text())
    return GoldApplication(**data)  # validation Pydantic = conformité M2 → M1

# M1 → tests/fixtures/json/isoclim.json
# {
#   "id": "isoclim",
#   "entities": [{"id": "client", "fields": [...], ...}]
# }

# M0 → isoclim/generated-project/apps/api/src/app/modules/client/model.py
# class Client(Base): ...
```
