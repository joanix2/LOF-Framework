from lof.reasoning.models import Fact, TruthStatus
from lof.silver.graph import SilverGraph

_VERB_NORMALIZE: dict[str, str] = {
    "voir": "read", "consulter": "read", "lire": "read", "afficher": "read",
    "créer": "create", "creer": "create", "ajouter": "create", "nouveau": "create",
    "modifier": "update", "éditer": "update", "editer": "update", "changer": "update",
    "supprimer": "delete", "effacer": "delete", "retirer": "delete", "enlever": "delete",
    "lister": "list", "afficher_tous": "list",
    "commenter": "comment", "répondre": "comment", "repondre": "comment",
    "valider": "validate", "approuver": "validate", "confirmer": "validate",
    "chercher": "search", "rechercher": "search", "trouver": "search",
}


class FactEncoder:
    def encode(self, silver: SilverGraph) -> list[Fact]:
        facts: list[Fact] = []

        for e in silver.entities.values():
            status: TruthStatus = "asserted" if e.status == "affirmed" else "hypothesized"
            facts.append(Fact(
                predicate="entity",
                args=(e.name.lower(),),
                status=status,
                bronze_ids=[p.bronze_id for p in e.provenance if p.bronze_id],
            ))
            facts.append(Fact(
                predicate="entity_type",
                args=(e.name.lower(), e.type),
                status=status,
            ))
            for k, v in e.attributes.items():
                facts.append(Fact(
                    predicate=k,
                    args=(e.name.lower(), str(v).lower()),
                    status=status,
                ))

        for c in silver.claims.values():
            status = ("asserted" if c.status == "affirmed" else "hypothesized" if c.status == "candidate" else "rejected")  # noqa: E501
            predicate = _VERB_NORMALIZE.get(c.predicate, c.predicate)
            is_norm = predicate in _VERB_NORMALIZE.values() and predicate != c.predicate
            pred = "permission" if is_norm else predicate
            f_args = (c.subject.lower(), predicate, c.object.lower()) if is_norm else (c.subject.lower(), c.object.lower())  # noqa: E501
            facts.append(Fact(
                predicate=pred,
                args=f_args,
                status=status,
                confidence=c.confidence,
                bronze_ids=[p.bronze_id for p in c.provenance if p.bronze_id],
                world="closed" if c.predicate in ("has_operation", "field_type") else "open",
            ))

        for r in silver.relations.values():
            status = "asserted" if r.status == "affirmed" else "hypothesized"
            facts.append(Fact(
                predicate=r.kind,
                args=(r.source.lower(), r.target.lower()),
                status=status,
                confidence=r.confidence,
                bronze_ids=[p.bronze_id for p in r.provenance if p.bronze_id],
            ))

        return facts
