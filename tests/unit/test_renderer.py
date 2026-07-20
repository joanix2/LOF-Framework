import tempfile
from pathlib import Path

from lof.rendering.jinja_renderer import JinjaRenderer


def test_render_simple():
    renderer = JinjaRenderer()
    result = renderer.render_from_string("Hello {{ name }}!", {"name": "World"})
    assert result == "Hello World!"


def test_render_snake_case_filter():
    renderer = JinjaRenderer()
    result = renderer.render_from_string("{{ name | snake_case }}", {"name": "HelloWorld"})
    assert result == "hello_world"


def test_render_camel_case_filter():
    renderer = JinjaRenderer()
    result = renderer.render_from_string("{{ name | camel_case }}", {"name": "hello_world"})
    assert result == "helloWorld"


def test_render_pascal_case_filter():
    renderer = JinjaRenderer()
    result = renderer.render_from_string("{{ name | pascal_case }}", {"name": "hello_world"})
    assert result == "HelloWorld"


def test_render_kebab_case_filter():
    renderer = JinjaRenderer()
    result = renderer.render_from_string("{{ name | kebab_case }}", {"name": "hello_world"})
    assert result == "hello-world"


def test_render_list():
    renderer = JinjaRenderer()
    result = renderer.render_from_string(
        "{% for item in items %}{{ item }}\n{% endfor %}",
        {"items": ["a", "b", "c"]},
    )
    assert result == "a\nb\nc\n"


def test_render_with_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpl_dir = Path(tmpdir)
        tmpl_file = tmpl_dir / "test.j2"
        tmpl_file.write_text("from {{ name | snake_case }} import {{ name }}")
        renderer = JinjaRenderer(tmpl_dir)
        output = renderer.render("test.j2", {"name": "HelloWorld"})
        assert "from hello_world import HelloWorld" in output
