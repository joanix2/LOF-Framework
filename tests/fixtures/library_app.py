"""Test fixture: Author/Book/Category — independent of LMP."""

from lof.models.gold_models import (
    GoldApplication,
    GoldCapabilities,
    GoldEntity,
    GoldField,
    GoldRelation,
)


def make_library_app() -> GoldApplication:
    return GoldApplication(
        id="library",
        name="Library Management",
        entities=[
            GoldEntity(
                id="author",
                name="Author",
                plural_name="Authors",
                description="Book author",
                display_field="name",
                fields=[
                    GoldField(
                        id="id", type="uuid", primary=True, generated=True,
                        list_visible=False, form_visible=False,
                    ),
                    GoldField(id="name", type="string", required=True,
                              searchable=True, sortable=True, max_length=200),
                    GoldField(id="biography", type="text",
                              form_visible=True, list_visible=False),
                    GoldField(id="birth_date", type="date",
                              form_visible=True, list_visible=False),
                    GoldField(id="active", type="boolean", default=True, list_visible=True),
                ],
                capabilities=GoldCapabilities(
                    create=True, read=True, update=True,
                    delete=True, list=True, search=True
                ),
            ),
            GoldEntity(
                id="book",
                name="Book",
                plural_name="Books",
                description="Published book",
                display_field="title",
                fields=[
                    GoldField(
                        id="id", type="uuid", primary=True, generated=True,
                        list_visible=False, form_visible=False,
                    ),
                    GoldField(id="title", type="string", required=True,
                              searchable=True, sortable=True, max_length=300),
                    GoldField(id="isbn", type="string", unique=True,
                              list_visible=True, max_length=20),
                    GoldField(id="publication_year", type="integer",
                              list_visible=True, sortable=True, minimum=1000, maximum=2100),
                    GoldField(id="pages", type="integer", list_visible=True, minimum=1),
                    GoldField(id="price", type="money", list_visible=True, minimum=0),
                ],
                relations=[
                    GoldRelation(
                        id="book_author", source="book", target="author",
                        kind="many-to-one", source_field="author_id",
                        target_display_field="name", required=True,
                        back_populates="author_books",
                    ),
                    GoldRelation(
                        id="book_category", source="book", target="category",
                        kind="many-to-one", source_field="category_id",
                        target_display_field="name", nullable=True,
                        back_populates="category_books",
                    ),
                ],
                capabilities=GoldCapabilities(
                    create=True, read=True, update=True,
                    delete=True, list=True, search=True
                ),
            ),
            GoldEntity(
                id="category",
                name="Category",
                plural_name="Categories",
                description="Book category",
                display_field="name",
                fields=[
                    GoldField(
                        id="id", type="uuid", primary=True, generated=True,
                        list_visible=False, form_visible=False,
                    ),
                    GoldField(id="name", type="string", required=True,
                              searchable=True, sortable=True, max_length=100),
                    GoldField(id="description", type="text",
                              form_visible=True, list_visible=False),
                ],
                capabilities=GoldCapabilities(
                    create=True, read=True, update=True,
                    delete=True, list=True, search=True
                ),
            ),
        ],
    )
