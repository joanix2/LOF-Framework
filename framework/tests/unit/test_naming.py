from lof.utils.naming import camel_case, kebab_case, pascal_case, pluralize, snake_case


def test_snake_case():
    assert snake_case("HelloWorld") == "hello_world"
    assert snake_case("hello-world") == "hello_world"
    assert snake_case("hello world") == "hello_world"
    assert snake_case("hello") == "hello"
    assert snake_case("") == ""


def test_camel_case():
    assert camel_case("hello_world") == "helloWorld"
    assert camel_case("HelloWorld") == "helloWorld"
    assert camel_case("hello-world") == "helloWorld"
    assert camel_case("hello") == "hello"


def test_pascal_case():
    assert pascal_case("hello_world") == "HelloWorld"
    assert pascal_case("hello-world") == "HelloWorld"
    assert pascal_case("hello") == "Hello"


def test_kebab_case():
    assert kebab_case("hello_world") == "hello-world"
    assert kebab_case("HelloWorld") == "hello-world"


def test_pluralize():
    assert pluralize("cat") == "cats"
    assert pluralize("box") == "boxes"
    assert pluralize("watch") == "watches"
    assert pluralize("city") == "cities"
    assert pluralize("day") == "days"
