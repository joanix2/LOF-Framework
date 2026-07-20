from pathlib import Path

from lof.silver.models import SilverClaim, SilverContradiction, SilverEntity, SilverRelation


class SilverGraph:
    def __init__(self):
        self.entities: dict[str, SilverEntity] = {}
        self.claims: dict[str, SilverClaim] = {}
        self.relations: dict[str, SilverRelation] = {}
        self.contradictions: dict[str, SilverContradiction] = {}
        self._dir: Path | None = None

    @classmethod
    def load(cls, root: Path) -> "SilverGraph":
        g = cls()
        g._dir = root / "data" / "silver"
        for d, store in [("entities", g.entities), ("claims", g.claims),
                          ("relations", g.relations), ("contradictions", g.contradictions)]:
            p = g._dir / d
            if p.exists():
                for f in sorted(p.glob("*.json")):
                    import json
                    data = json.loads(f.read_text())
                    if d == "entities":
                        obj = SilverEntity(**data)
                    elif d == "claims":
                        obj = SilverClaim(**data)
                    elif d == "relations":
                        obj = SilverRelation(**data)
                    else:
                        obj = SilverContradiction(**data)
                    store[obj.id] = obj
        return g

    def save(self, root: Path) -> None:
        self._dir = root / "data" / "silver"
        for d, store in [("entities", self.entities), ("claims", self.claims),
                          ("relations", self.relations), ("contradictions", self.contradictions)]:
            p = self._dir / d
            p.mkdir(parents=True, exist_ok=True)
            for obj in store.values():
                import json
                (p / f"{obj.id}.json").write_text(json.dumps(
                    obj.model_dump(), indent=2, default=str))

    def add_claim(self, claim: SilverClaim) -> None:
        self.claims[claim.id] = claim
        self._check_contradictions(claim)

    def _check_contradictions(self, claim: SilverClaim) -> None:
        for other in self.claims.values():
            if other.id == claim.id:
                continue
            if other.subject == claim.subject and other.predicate == claim.predicate:
                if other.object != claim.object and other.status == "affirmed":
                    cid = f"contra_{claim.id}_{other.id}"
                    if cid not in self.contradictions:
                        self.contradictions[cid] = SilverContradiction(
                            id=cid,
                            claim_ids=[claim.id, other.id],
                            description=f"'{claim.subject} {claim.predicate}' targets both "
                                        f"'{claim.object}' and '{other.object}'",
                            severity="error",
                        )
                elif other.object == claim.object and other.status != claim.status:
                    cid = f"contra_status_{claim.id}_{other.id}"
                    if cid not in self.contradictions:
                        self.contradictions[cid] = SilverContradiction(
                            id=cid,
                            claim_ids=[claim.id, other.id],
                            description=f"'{claim.subject} {claim.predicate} {claim.object}' "
                                        f"status conflict: {other.status} vs {claim.status}",
                            severity="warning",
                        )

    def get_claims_for_subject(self, subject: str) -> list[SilverClaim]:
        return [c for c in self.claims.values() if c.subject == subject]

    def resolve_contradiction(self, contradiction_id: str, resolution: str) -> None:
        if contradiction_id in self.contradictions:
            self.contradictions[contradiction_id].resolved = True
            self.contradictions[contradiction_id].resolution = resolution
