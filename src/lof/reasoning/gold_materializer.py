import json
from pathlib import Path
from typing import Any

from lof.reasoning.models import ReasoningResult, Rule


class GoldMaterializer:
    def __init__(self, rules: list[Rule]):
        self.rules = rules

    def materialize(self, result: ReasoningResult) -> list[dict[str, Any]]:
        entities: dict[str, dict[str, Any]] = {}
        fact_map = {f.key: f for f in result.facts}

        for f in result.facts:
            if f.status in ("rejected", "contradicted"):
                continue
            if f.predicate != "entity":
                continue
            eid = f.args[0]
            if eid not in entities:
                entities[eid] = {
                    "id": eid,
                    "name": eid.capitalize(),
                    "fields": [],
                    "operations": [],
                    "relations": [],
                    "projections": [],
                }  # noqa: E501

        for f in result.facts:
            if f.status in ("rejected", "contradicted"):
                continue
            eid = f.args[0] if f.args else ""
            if eid not in entities:
                continue

            if f.predicate == "field_type" and len(f.args) >= 2:
                field = {"name": f.args[0], "type": f.args[1], "required": False}
                if f.key in fact_map:
                    for rel_fact_key in fact_map:
                        rfk = fact_map[rel_fact_key]
                        if (
                            rfk.predicate == "required"
                            and len(rfk.args) >= 2
                            and rfk.args[0] == f.args[0]
                        ):  # noqa: E501
                            field["required"] = True
                entities[eid]["fields"].append(field)

            elif f.predicate == "has_operation" and len(f.args) >= 2:
                if f.args[1] not in entities[eid]["operations"]:
                    entities[eid]["operations"].append(f.args[1])

            elif f.predicate in ("many_to_one", "one_to_one") and len(f.args) >= 2:
                rel = {
                    "id": f"{eid}-{f.args[1]}",
                    "kind": f.predicate.replace("_", "-"),
                    "target": f.args[1],
                    "sourceField": f"{f.args[1]}_id",
                    "targetField": "id",
                    "inverse": None,
                    "required": True,
                }
                entities[eid]["relations"].append(rel)

            elif f.predicate == "requires_projection" and len(f.args) >= 2:
                if f.args[1] not in entities[eid]["projections"]:
                    entities[eid]["projections"].append(f.args[1])

        for eid, ent in entities.items():
            if not ent["fields"]:
                ent["fields"] = [{"name": "id", "type": "uuid", "primary": True, "generated": True}]
            if not any(f.get("primary") for f in ent["fields"]):
                ent["fields"].insert(
                    0,
                    {
                        "name": "id",
                        "type": "uuid",  # noqa: E501
                        "primary": True,
                        "generated": True,
                    },
                )
            if not ent["operations"]:
                ent["operations"] = ["create", "read", "update", "delete", "list"]

        return list(entities.values())

    def write_gold(self, entities: list[dict[str, Any]], output_dir: Path) -> list[Path]:
        written: list[Path] = []
        gold_dir = output_dir / "data" / "gold" / "instances"
        gold_dir.mkdir(parents=True, exist_ok=True)
        for ent in entities:
            path = gold_dir / f"{ent['id']}.json"
            path.write_text(
                json.dumps(
                    {
                        "id": ent["id"],
                        "type": "entity-model",
                        "values": {
                            "name": ent["name"],
                            "pluralName": ent["name"] + "s",
                            "route": ent["id"],
                            "tableName": ent["id"],
                            "fields": ent["fields"],
                            "operations": ent["operations"],
                        },
                        "relations": ent.get("relations", []),
                    },
                    indent=2,
                )
            )
            written.append(path)
        return written
