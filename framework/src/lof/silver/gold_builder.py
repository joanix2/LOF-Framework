import json
from pathlib import Path
from typing import Any

from lof.silver.graph import SilverGraph


class GoldCandidateBuilder:
    def __init__(self, silver: SilverGraph):
        self.silver = silver

    def build_gold_instances(self) -> list[dict[str, Any]]:
        entities = self._resolve_entities()
        instances: list[dict[str, Any]] = []

        for ent in entities:
            fields = self._resolve_fields(ent)
            operations = self._resolve_operations(ent)
            relations = self._resolve_relations(ent)
            route = ent.get("name", ent.get("id", "unknown"))
            table = ent.get("table_name", route)

            instance: dict[str, Any] = {
                "id": ent.get("id"),
                "type": "entity-model",
                "values": {
                    "name": ent.get("name", ent["id"]),
                    "pluralName": ent.get("plural_name", ent.get("name", ent["id"]) + "s"),
                    "route": route,
                    "tableName": table,
                    "fields": fields,
                    "operations": operations or ["create", "read", "update", "delete", "list"],
                },
            }

            if relations:
                instance["relations"] = relations

            instances.append(instance)

        return instances

    def _resolve_entities(self) -> list[dict[str, Any]]:
        entities: dict[str, dict[str, Any]] = {}
        for ent in self.silver.entities.values():
            if ent.status == "refuted":
                continue
            entities[ent.id] = {
                "id": ent.id,
                "name": ent.name,
                "type": ent.type,
                **{k: v for k, v in ent.attributes.items()},
            }

        for claim in self.silver.claims.values():
            if claim.status not in ("affirmed", "candidate"):
                continue
            if claim.predicate == "has_field" and claim.subject in entities:
                entities[claim.subject].setdefault("_fields", []).append(claim.object)
            if claim.predicate == "has_operation" and claim.subject in entities:
                entities[claim.subject].setdefault("_operations", []).append(claim.object)
            if claim.predicate == "has_relation" and claim.subject in entities:
                entities[claim.subject].setdefault("_raw_relations", []).append({
                    "target": claim.object,
                    "kind": claim.metadata.get("kind", "many-to-one"),
                })

        return list(entities.values())

    def _resolve_fields(self, entity: dict[str, Any]) -> list[dict[str, Any]]:
        fields: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        for claim in self.silver.claims.values():
            if claim.status == "refuted":
                continue
            if claim.predicate != "has_field":
                continue
            obj = claim.object if isinstance(claim.object, str) else ""
            if obj not in seen_names:
                seen_names.add(obj)

        for claim in self.silver.claims.values():
            if claim.status == "refuted":
                continue
            if claim.predicate == "field_type" and claim.subject in seen_names:
                ftype = claim.object if isinstance(claim.object, str) else "string"
                fields.append({
                    "name": claim.subject,
                    "type": ftype,
                    "required": claim.metadata.get("required", False),
                    "primary": claim.metadata.get("primary", False),
                })

        if not fields:
            fields.append({"name": "id", "type": "uuid", "primary": True, "generated": True})

        return fields

    def _resolve_operations(self, entity: dict[str, Any]) -> list[str]:
        ops = entity.get("_operations", [])
        base = ["create", "read", "update", "delete", "list"]
        return list(dict.fromkeys(base + ops))

    def _resolve_relations(self, entity: dict[str, Any]) -> list[dict[str, Any]]:
        relations: list[dict[str, Any]] = []
        for rr in entity.get("_raw_relations", []):
            relations.append({
                "id": f"{entity['id']}-{rr['target']}",
                "kind": rr.get("kind", "many-to-one"),
                "target": rr["target"],
                "sourceField": f"{rr['target']}_id" if rr.get("kind") == "many-to-one" else None,
                "targetField": "id",
                "inverse": rr.get("inverse"),
                "required": rr.get("required", True),
            })
        return relations

    def write_gold_candidate(self, output_dir: Path) -> list[Path]:
        instances = self.build_gold_instances()
        written: list[Path] = []
        gold_dir = output_dir / "data" / "gold" / "instances"
        gold_dir.mkdir(parents=True, exist_ok=True)
        for inst in instances:
            path = gold_dir / f"{inst['id']}.json"
            path.write_text(json.dumps(inst, indent=2))
            written.append(path)
        return written
