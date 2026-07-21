"""Tests for Gold entity projection and instance generation."""

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
    ent = GoldEntity(
        id="client",
        name="Client",
        fields=[
            GoldField(id="id", type="uuid", primary=True, generated=True, list_visible=False),
            GoldField(id="name", type="string", required=True, searchable=True),
            GoldField(id="email", type="email", required=True, unique=True),
        ],
    )
    projector = EntityProjector()
    proj = projector.project(ent)
    assert proj.name == "Client"
    assert len(proj.fields) == 3
    assert proj.fields[1].type == "string"
    assert proj.fields[1].py_type == "str"
    assert proj.fields[1].required is True
    assert proj.fields[1].searchable is True


def test_project_entity_with_operations():
    ent = GoldEntity(
        id="project",
        name="Project",
        capabilities=GoldCapabilities(create=True, list=True, delete=False),
    )
    projector = EntityProjector()
    proj = projector.project(ent)
    assert "create" in proj.operations
    assert "list" in proj.operations
    assert "delete" not in proj.operations


def test_project_relation_many_to_one():
    author = GoldEntity(id="author", name="Author")
    book = GoldEntity(
        id="book",
        name="Book",
        relations=[
            GoldRelation(
                id="book_author",
                source="book",
                target="author",
                kind="many-to-one",
                source_field="author_id",
                target_display_field="name",
                required=True,
            ),
        ],
    )
    projector = EntityProjector()
    proj = projector.project(book, [author, book])
    assert len(proj.relations) == 1
    assert proj.relations[0].kind == "many-to-one"
    assert proj.relations[0].source_field == "author_id"


def test_project_incoming_relation():
    author = GoldEntity(id="author", name="Author")
    book = GoldEntity(
        id="book",
        name="Book",
        relations=[
            GoldRelation(
                id="book_author",
                source="book",
                target="author",
                kind="many-to-one",
                source_field="author_id",
                back_populates="author_books",
            ),
        ],
    )
    projector = EntityProjector()
    proj = projector.project(author, [author, book])
    assert len(proj.incoming_relations) == 1
    assert proj.incoming_relations[0].kind == "one-to-many"


def test_field_type_mapping():
    ent = GoldEntity(
        id="t",
        fields=[
            GoldField(id="s", type="string"),
            GoldField(id="i", type="integer"),
            GoldField(id="b", type="boolean"),
            GoldField(id="d", type="date"),
            GoldField(id="e", type="email"),
        ],
    )
    proj = EntityProjector().project(ent)
    types = {f.name: f.py_type for f in proj.fields}
    assert types["s"] == "str"
    assert types["i"] == "int"
    assert types["b"] == "bool"
    assert types["d"] == "datetime"
    assert types["e"] == "EmailStr"


def test_instance_generation():
    app = make_library_app()
    with tempfile.TemporaryDirectory() as tmp:
        gen = GoldInstanceGenerator(app)
        paths = gen.generate(Path(tmp))
        assert len(paths) == 3  # author, book, category
        import json

        for p in paths:
            data = json.loads(p.read_text())
            assert data["type"] == "entity-model"
            assert "values" in data
            assert "fields" in data["values"]


def test_library_entity_count():
    app = make_library_app()
    assert len(app.entities) == 3
    ids = [e.id for e in app.entities]
    assert "author" in ids
    assert "book" in ids
    assert "category" in ids


def test_book_relations():
    app = make_library_app()
    book = next(e for e in app.entities if e.id == "book")
    assert len(book.relations) == 1
    assert book.relations[0].target == "author"
    assert book.relations[0].kind == "many-to-one"
