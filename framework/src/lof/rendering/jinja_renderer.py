from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from lof.utils.naming import camel_case, kebab_case, pascal_case, pluralize, snake_case


class JinjaRenderer:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self._env: Environment | None = None

    def _get_env(self) -> Environment:
        if self._env is None:
            self._env = Environment(
                loader=FileSystemLoader(str(self.root)),
                undefined=StrictUndefined,
            )
            self._env.filters["snake_case"] = snake_case
            self._env.filters["camel_case"] = camel_case
            self._env.filters["pascal_case"] = pascal_case
            self._env.filters["kebab_case"] = kebab_case
            self._env.filters["pluralize"] = pluralize
        return self._env

    def render(self, template_path: str, context: dict[str, Any]) -> str:
        env = self._get_env()
        try:
            template = env.get_template(template_path)
            return template.render(**context)
        except TemplateNotFound:
            alt_path = str(self.root / template_path)
            try:
                with open(alt_path) as f:
                    content = f.read()
                from jinja2 import Template

                tmpl = Template(content)
                return tmpl.render(**context)
            except FileNotFoundError:
                raise FileNotFoundError(f"Template not found: {template_path}")

    def render_from_string(self, template_str: str, context: dict[str, Any]) -> str:
        env = Environment(undefined=StrictUndefined)
        env.filters["snake_case"] = snake_case
        env.filters["camel_case"] = camel_case
        env.filters["pascal_case"] = pascal_case
        env.filters["kebab_case"] = kebab_case
        env.filters["pluralize"] = pluralize
        template = env.from_string(template_str)
        return template.render(**context)
