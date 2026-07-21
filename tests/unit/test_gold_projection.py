"""Tests for Gold entity projection — pure data, no type mappings."""

import tempfile
from pathlib import Path

from lof.gold.instance_generator import GoldInstanceGenerator
from lof.gold.projection import EntityProjector
from lof.models.gold_models import (
    GoldCapabilities,
    GoldEntity,
    GoldField,
    GoldRelation,
)
from tests.fixtures.library_app import make_library_app


def test_project_entity():
    ent = GoldEntity(id="client", name="Client", fields=[
        GoldField(id="id", type="uuid", primary=True, generated=True, list_visible=False),
        GoldField(id="name", type="string", required=True, searchable=True),
        GoldField(id="email", type="email", required=True, unique=True),
    ])
    ctx = EntityProjector().project(ent)
    assert ctx["name"] == "Client"
    assert len(ctx["fields"]) == 3
    fields = {f["name"]: f for f in ctx["fields"]}
    assert fields["name"]["type"] == "string"
    assert fields["name"]["required"] is True
    assert fields["name"]["searchable"] is True
    assert fields["email"]["unique"] is True


def test_project_entity_with_operations():
    cap = GoldCapabilities(create=True, list=True, delete=False)
    ent = GoldEntity(id="project", capabilities=cap)
    ctx = EntityProjector().project(ent)
    assert "create" in ctx["operations"]
    assert "list" in ctx["operations"]
    assert "delete" not in ctx["operations"]


def test_project_relation_many_to_one():
    book = GoldEntity(id="book", relations=[
        GoldRelation(id="book_author", source="book", target="author",
                     kind="many-to-one", source_field="author_id",
                     target_display_field="name", required=True),
    ])
    ctx = EntityProjector().project(book, [GoldEntity(id="author"), book])
    assert len(ctx["relations"]) == 1
    assert ctx["relations"][0]["kind"] == "many-to-one"
    assert ctx["relations"][0]["source_field"] == "author_id"


def test_project_incoming_relation():
    author = GoldEntity(id="author")
    book = GoldEntity(id="book", relations=[
        GoldRelation(id="book_author", source="book", target="author",
                     kind="many-to-one", back_populates="author_books"),
    ])
    ctx = EntityProjector().project(author, [author, book])
    assert len(ctx["incoming_relations"]) == 1
    assert ctx["incoming_relations"][0]["kind"] == "one-to-many"


def test_field_types_preserved():
    ent = GoldEntity(id="t", fields=[
        GoldField(id="s", type="string"), GoldField(id="i", type="integer"),
        GoldField(id="b", type="boolean"), GoldField(id="d", type="date"),
        GoldField(id="e", type="email"), GoldField(id="m", type="money"),
    ])
    ctx = EntityProjector().project(ent)
    types = {f["name"]: f["type"] for f in ctx["fields"]}
    assert types["s"] == "string"
    assert types["i"] == "integer"
    assert types["b"] == "boolean"
    assert types["d"] == "date"
    assert types["e"] == "email"
    assert types["m"] == "money"  # template handles mapping


def test_instance_generation():
    app = make_library_app()
    with tempfile.TemporaryDirectory() as tmp:
        gen = GoldInstanceGenerator(app)
        paths = gen.generate(Path(tmp))
        assert len(paths) == 3
        import json
        for p in paths:
            data = json.loads(p.read_text())
            assert data["type"] == "entity-model"
            assert "values" in data
            assert "fields" in data["values"]


def test_library_entity_count():
    app = make_library_app()
    assert len(app.entities) == 3


def test_book_relation_preserved():
    app = make_library_app()
    with tempfile.TemporaryDirectory() as tmp:
        tmp_p = Path(tmp)
        GoldInstanceGenerator(app).generate(tmp_p)
        import json
        book_path = tmp_p / "data" / "gold" / "instances" / "book.json"
        book = json.loads(book_path.read_text())
        assert len(book["relations"]) == 2
        targets = [r["target"] for r in book["relations"]]
        assert "author" in targets
        assert "category" in targets
