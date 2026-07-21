"""Admin CRUD profile generator — reads LOF Registry, generates backend + frontend."""

from lof.admin.generators.backend import generate_all as gen_backend
from lof.admin.generators.frontend import generate_all as gen_frontend
from lof.admin.schema.adapter import AdminApp

ADMIN_CRUD_RULES = []


def generate(registry) -> dict[str, str]:
    app = AdminApp(registry)
    files = {}
    files.update(gen_backend(app))
    files.update(gen_frontend(app))
    return files
