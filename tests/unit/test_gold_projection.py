"""Tests for Gold entity projection — pure data from JSON DSL."""

import json
import tempfile
from pathlib import Path

from lof.gold.instance_generator import GoldInstanceGenerator
from lof.gold.json_loader import load_gold_application
from lof.gold.projection import EntityProjector
from lof.models.gold_models import GoldCapabilities, ModelDef, AttributeDef, GoldRelation

LIBRARY_JSON = Path(__file__).resolve().parent.parent.parent / "programs" / "library" / "library.json"
ISOCLIM_JSON = Path(__file__).resolve().parent.parent.parent / "programs" / "isoclim" / "isoclim.json"


def test_project_entity():
    ent = ModelDef(id="client", name="Client", fields=[
        AttributeDef(id="id", type="uuid", primary=True, generated=True, list_visible=False),
        AttributeDef(id="name", type="string", required=True, searchable=True),
        AttributeDef(id="email", type="email", required=True, unique=True),
    ])
    ctx = EntityProjector().project(ent)
    assert ctx["name"] == "Client"
    assert len(ctx["fields"]) == 3
    fields = {f["name"]: f for f in ctx["fields"]}
    assert fields["name"]["type"] == "string"
    assert fields["name"]["required"] is True
    assert fields["email"]["unique"] is True


def test_project_entity_with_operations():
    cap = GoldCapabilities(create=True, list=True, delete=False)
    ent = ModelDef(id="project", capabilities=cap)
    ctx = EntityProjector().project(ent)
    assert "create" in ctx["operations"]
    assert "list" in ctx["operations"]
    assert "delete" not in ctx["operations"]


def test_project_relation_many_to_one():
    book = ModelDef(id="book", relations=[
        GoldRelation(id="book_author", source="book", target="author",
                     kind="many-to-one", source_field="author_id",
                     target_display_field="name", required=True),
    ])
    ctx = EntityProjector().project(book, [ModelDef(id="author"), book])
    assert len(ctx["relations"]) == 1
    assert ctx["relations"][0]["kind"] == "many-to-one"
    assert ctx["relations"][0]["source_field"] == "author_id"


def test_project_incoming_relation():
    author = ModelDef(id="author")
    book = ModelDef(id="book", relations=[
        GoldRelation(id="book_author", source="book", target="author",
                     kind="many-to-one", back_populates="author_books"),
    ])
    ctx = EntityProjector().project(author, [author, book])
    assert len(ctx["incoming_relations"]) == 1
    assert ctx["incoming_relations"][0]["kind"] == "one-to-many"


def test_field_types_preserved():
    ent = ModelDef(id="t", fields=[
        AttributeDef(id="s", type="string"), AttributeDef(id="i", type="integer"),
        AttributeDef(id="b", type="boolean"), AttributeDef(id="d", type="date"),
        AttributeDef(id="e", type="email"), AttributeDef(id="m", type="money"),
    ])
    ctx = EntityProjector().project(ent)
    types = {f["name"]: f["type"] for f in ctx["fields"]}
    assert types["s"] == "string"
    assert types["m"] == "money"


def test_instance_generation_from_json():
    app = load_gold_application(LIBRARY_JSON)
    assert len(app.entities) == 3
    with tempfile.TemporaryDirectory() as tmp:
        gen = GoldInstanceGenerator(app)
        paths = gen.generate(Path(tmp))
        assert len(paths) == 3  # one instance per entity
        for p in paths:
            data = json.loads(p.read_text())
            assert data["type"] == "entity"


def test_book_relation_from_json():
    app = load_gold_application(LIBRARY_JSON)
    with tempfile.TemporaryDirectory() as tmp:
        GoldInstanceGenerator(app).generate(Path(tmp))
        book_path = Path(tmp) / ".lof" / "instances" / "book.json"
        book = json.loads(book_path.read_text())
        rels = book.get("relations", [])
        assert len(rels) == 2
        targets = [r["target"] for r in rels]
        assert "author-model" in targets
        assert "category-model" in targets


def test_isoclim_loaded_from_json():
    app = load_gold_application(ISOCLIM_JSON)
    assert len(app.entities) == 8
    ids = [e.id for e in app.entities]
    assert "client" in ids
    assert "mission" in ids
    assert "equipement" in ids


def test_isoclim_generates_instances():
    app = load_gold_application(ISOCLIM_JSON)
    with tempfile.TemporaryDirectory() as tmp:
        paths = GoldInstanceGenerator(app).generate(Path(tmp))
        assert len(paths) == 8  # 8 entities, one instance each
