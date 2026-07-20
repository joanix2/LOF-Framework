import re
from uuid import uuid4

from lof.bronze.models import BronzeEntry
from lof.silver.graph import SilverGraph
from lof.silver.models import ProvenanceRef, SilverClaim, SilverEntity


class IntentExtractor:
    def __init__(self, silver: SilverGraph):
        self.silver = silver

    def extract_from_entry(self, entry: BronzeEntry) -> list[SilverClaim]:
        claims: list[SilverClaim] = []
        text = entry.content.lower()

        entity_patterns = [
            (r"(?:entité|entity|resource|module)\s+(\w+)", "entity"),
            (r"(?:un|une|des)\s+(\w+)\s+(?:a|possède|doit|peut)", "entity"),
            (r"les\s+(\w+)\s+(?:puissent|peuvent|doivent)", "entity"),
            (r"(?:voir|commenter|valider|créer|modifier)\s+(?:un|une|des|leur)?\s*(\w+)", "entity"),
        ]

        field_patterns = [
            (r"(\w+)\s+(\w+)\s*(?:obligatoire|requis|required)", "field_required"),
            (r"(\w+)\s+(\w+)\s*(?:optionnel|optional)", "field_optional"),
            (r"(\w+)\s+(?:a|possède)\s+(?:un|une|des)\s+(\w+)", "field"),
        ]

        operation_patterns = [
            (r"(?:puissent|peuvent|pouvoir|peut|can)\s+(\w+)", "operation"),
            (r"(?:pour|to)\s+(\w+)\s+(?:un|une|des|les)?\s*(\w+)", "operation"),
            (r"(?:CRUD|crud|list|create|read|update|delete|search)\s+(\w+)", "operation"),
        ]

        for pattern, kind in entity_patterns:
            for m in re.finditer(pattern, text):
                name = m.group(1).capitalize().rstrip(".,;:!?")
                if len(name) > 2 and name not in ("Les", "Des", "Un", "Une", "Le", "La"):
                    eid = f"ent_{name.lower()}_{uuid4().hex[:6]}"
                    if eid not in self.silver.entities:
                        self.silver.entities[eid] = SilverEntity(
                            id=eid, name=name, type=kind, status="candidate",
                            provenance=[ProvenanceRef(bronze_id=entry.id, span=m.group(0))],
                        )

        for pattern, kind in field_patterns:
            for m in re.finditer(pattern, text):
                fname = m.group(2).rstrip(".,;:!?")
                claims.append(SilverClaim(
                    id=f"claim_{uuid4().hex[:8]}",
                    subject=m.group(1).capitalize(),
                    predicate="field_type",
                    object=fname,
                    status="candidate",
                    metadata={"required": kind == "field_required"},
                    provenance=[ProvenanceRef(bronze_id=entry.id, span=m.group(0))],
                ))

        for pattern, kind in operation_patterns:
            for m in re.finditer(pattern, text):
                verb = m.group(1).rstrip(".,;:!?")
                obj = (m.group(2).capitalize().rstrip(".,;:!?") if m.lastindex and m.lastindex >= 2 else "")  # noqa: E501
                sub = obj if obj else ""
                claims.append(SilverClaim(
                    id=f"claim_{uuid4().hex[:8]}",
                    subject=sub,
                    predicate="has_operation",
                    object=verb,
                    status="candidate",
                    provenance=[ProvenanceRef(bronze_id=entry.id, span=m.group(0))],
                ))

        return claims
