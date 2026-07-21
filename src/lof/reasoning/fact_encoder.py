"""Encodes Silver graph facts into logical facts for the Datalog engine.

Verb normalization and closed-world predicates come from the Profile config.
No hardcoded mappings.
"""

from lof.gold.profile import Profile
from lof.reasoning.models import Fact, TruthStatus
from lof.silver.graph import SilverGraph


class FactEncoder:
    def __init__(self, profile: Profile | None = None):
        self.profile = profile

    def encode(self, silver: SilverGraph) -> list[Fact]:
        facts: list[Fact] = []
        verb_norm: dict[str, str] = {}
        closed_world: set[str] = set()

        if self.profile:
            verb_norm = self.profile.verb_normalization
            closed_world = self.profile.closed_world_predicates

        for e in silver.entities.values():
            status: TruthStatus = "asserted" if e.status == "affirmed" else "hypothesized"
            facts.append(
                Fact(
                    predicate="entity",
                    args=(e.name.lower(),),
                    status=status,
                    bronze_ids=[p.bronze_id for p in e.provenance if p.bronze_id],
                )
            )
            facts.append(
                Fact(
                    predicate="entity_type",
                    args=(e.name.lower(), e.type),
                    status=status,
                )
            )
            for k, v in e.attributes.items():
                facts.append(
                    Fact(
                        predicate=k,
                        args=(e.name.lower(), str(v).lower()),
                        status=status,
                    )
                )

        for c in silver.claims.values():
            status = (
                "asserted"
                if c.status == "affirmed"
                else "hypothesized"
                if c.status == "candidate"
                else "rejected"
            )  # noqa: E501
            predicate = verb_norm.get(c.predicate, c.predicate)
            is_norm = predicate in verb_norm.values() and predicate != c.predicate
            pred = "permission" if is_norm else predicate
            args = (
                (c.subject.lower(), predicate, c.object.lower())
                if is_norm
                else (c.subject.lower(), c.object.lower())
            )  # noqa: E501
            facts.append(
                Fact(
                    predicate=pred,
                    args=args,
                    status=status,
                    confidence=c.confidence,
                    bronze_ids=[p.bronze_id for p in c.provenance if p.bronze_id],
                    world="closed" if predicate in closed_world else "open",
                )
            )

        for r in silver.relations.values():
            status = "asserted" if r.status == "affirmed" else "hypothesized"
            facts.append(
                Fact(
                    predicate=r.kind,
                    args=(r.source.lower(), r.target.lower()),
                    status=status,
                    confidence=r.confidence,
                    bronze_ids=[p.bronze_id for p in r.provenance if p.bronze_id],
                )
            )

        return facts
