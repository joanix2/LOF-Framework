from uuid import uuid4

import spacy
from spacy.tokens import Doc

from lof.bronze.models import BronzeEntry
from lof.silver.graph import SilverGraph
from lof.silver.models import ProvenanceRef, SilverClaim, SilverEntity


class SpacyExtractor:
    def __init__(self, silver: SilverGraph, model: str = "fr_core_news_sm"):
        self.silver = silver
        self.nlp = spacy.load(model)

    def extract_from_entry(self, entry: BronzeEntry) -> list[SilverClaim]:
        claims: list[SilverClaim] = []
        doc = self.nlp(entry.content)

        self._extract_entities_from_noun_chunks(doc, entry)
        claims.extend(self._extract_verb_chain_triples(doc, entry))
        claims.extend(self._extract_prepositional_relations(doc, entry))

        return claims

    def _add_entity(self, name: str, entry: BronzeEntry, span: str | None = None) -> str:
        name = name.strip().capitalize().rstrip(".,;:!?")
        if len(name) <= 2:
            return ""
        existing = [e for e in self.silver.entities.values() if e.name == name]
        if existing:
            return name
        eid = f"ent_{name.lower()}_{uuid4().hex[:6]}"
        self.silver.entities[eid] = SilverEntity(
            id=eid,
            name=name,
            type="concept",
            status="candidate",
            provenance=[ProvenanceRef(bronze_id=entry.id, span=span or name)],
        )
        return name

    def _extract_entities_from_noun_chunks(self, doc: Doc, entry: BronzeEntry) -> None:
        for chunk in doc.noun_chunks:
            name = chunk.root.text.strip().capitalize().rstrip(".,;:!?")
            if len(name) > 2 and chunk.root.pos_ in ("NOUN", "PROPN"):
                self._add_entity(name, entry, chunk.text)
        for ent in doc.ents:
            name = ent.text.strip().capitalize()
            if len(name) > 2:
                existing = [e for e in self.silver.entities.values() if e.name == name]
                if not existing:
                    eid = f"ent_{name.lower()}_{uuid4().hex[:6]}"
                    self.silver.entities[eid] = SilverEntity(
                        id=eid,
                        name=name,
                        type=f"ner_{ent.label_}",
                        status="candidate",
                        provenance=[ProvenanceRef(bronze_id=entry.id, span=ent.text)],
                    )

    def _extract_verb_chain_triples(self, doc: Doc, entry: BronzeEntry) -> list[SilverClaim]:
        claims: list[SilverClaim] = []

        def walk_verbs(token, context_subject: str = "", context_verb: str = ""):
            if token.pos_ != "VERB" and token.dep_ != "ROOT":
                return

            subjects = [c for c in token.children if c.dep_ in ("nsubj", "nsubj:pass")]
            subj = (
                subjects[0].text.strip().capitalize().rstrip(".,;:!?")
                if subjects
                else context_subject
            )  # noqa: E501

            if subj and len(subj) > 2:
                self._add_entity(subj, entry)

            objects = [c for c in token.children if c.dep_ in ("obj", "dobj", "attr")]
            obliques = [c for c in token.children if c.dep_ in ("obl", "obl:arg")]
            obj_text = objects[0].text.strip().capitalize().rstrip(".,;:!?") if objects else ""
            obl_text = obliques[0].text.strip().capitalize().rstrip(".,;:!?") if obliques else ""

            full_obj = obj_text or obl_text or ""
            if full_obj and len(full_obj) > 2:
                self._add_entity(full_obj, entry)

            xcomps = [c for c in token.children if c.dep_ == "xcomp" and c.pos_ == "VERB"]
            conj_verbs = [
                c for c in token.children if c.dep_ in ("conj", "ccomp") and c.pos_ == "VERB"
            ]  # noqa: E501
            sub_verbs = xcomps + conj_verbs

            if sub_verbs:
                for sv in sub_verbs:
                    walk_verbs(sv, subj, token.lemma_)
            else:
                verb = token.lemma_
                if subj and full_obj:
                    claims.append(
                        SilverClaim(
                            id=f"claim_{uuid4().hex[:8]}",
                            subject=subj,
                            predicate=verb,
                            object=full_obj,
                            status="candidate",
                            provenance=[ProvenanceRef(bronze_id=entry.id, span=token.text)],
                        )
                    )
                elif subj and not full_obj:
                    obj_from_prep = self._find_prepositional_object(token)
                    if obj_from_prep:
                        claims.append(
                            SilverClaim(
                                id=f"claim_{uuid4().hex[:8]}",
                                subject=subj,
                                predicate=verb,
                                object=obj_from_prep,
                                status="candidate",
                                provenance=[ProvenanceRef(bronze_id=entry.id, span=token.text)],
                            )
                        )

        for token in doc:
            if token.dep_ == "ROOT":
                walk_verbs(token)
                break

        return claims

    def _find_prepositional_object(self, token) -> str:
        for child in token.children:
            if child.dep_ == "obl" or child.dep_ == "obl:arg":
                for grandchild in child.children:
                    if grandchild.dep_ in ("obj", "pobj") or grandchild.pos_ == "NOUN":
                        return grandchild.text.strip().capitalize()
        return ""

    def _extract_prepositional_relations(self, doc: Doc, entry: BronzeEntry) -> list[SilverClaim]:
        claims: list[SilverClaim] = []
        for token in doc:
            if token.dep_ in ("obl", "obl:arg") and token.pos_ == "NOUN":
                head = token.head
                if head.pos_ == "VERB":
                    subjects = [c for c in head.children if c.dep_ in ("nsubj", "nsubj:pass")]
                    subj = subjects[0].text.strip().capitalize() if subjects else ""
                    obj = token.text.strip().capitalize()
                    if subj and obj and len(obj) > 2:
                        self._add_entity(subj, entry)
                        self._add_entity(obj, entry)
                        claims.append(
                            SilverClaim(
                                id=f"claim_{uuid4().hex[:8]}",
                                subject=subj,
                                predicate=head.lemma_,
                                object=obj,
                                status="candidate",
                                provenance=[ProvenanceRef(bronze_id=entry.id, span=token.text)],
                            )
                        )
        return claims
