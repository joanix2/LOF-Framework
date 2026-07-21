"""Generates FastAPI backend code from the intermediate schema."""

from lof.admin.schema.models import ApplicationSchema, ModelField, ModelSchema


def generate_model(model: ModelSchema) -> str:
    lines = ["from datetime import date, datetime", "from uuid import UUID, uuid4", "from pydantic import BaseModel", 'from sqlalchemy import Column, String, Integer, Float, Boolean, Date, DateTime, Enum, Text, ForeignKey', 'from sqlalchemy.orm import relationship', 'from sqlalchemy.dialects.postgresql import UUID as SA_UUID', "", "Base = declarative_base()", ""]
    imports_done = True

    lines.append(f"class {model.name}(Base):")
    lines.append(f'    __tablename__ = "{model.table_name}"')
    lines.append("")
    for field in model.fields:
        if field.primary_key and field.generated:
            lines.append(f"    {field.name} = Column(SA_UUID, primary_key=True, default=uuid4)")
        elif field.type == "string":
            max_l = field.max_length or 255
            lines.append(f"    {field.name} = Column(String({max_l}){', nullable=False' if field.required else ''})")
        elif field.type == "text":
            lines.append(f"    {field.name} = Column(Text{', nullable=False' if field.required else ''})")
        elif field.type == "integer":
            lines.append(f"    {field.name} = Column(Integer{', nullable=False' if field.required else ''})")
        elif field.type == "float":
            lines.append(f"    {field.name} = Column(Float{', nullable=False' if field.required else ''})")
        elif field.type == "boolean":
            lines.append(f"    {field.name} = Column(Boolean, default={str(field.default).lower() if field.default is not None else 'False'})")
        elif field.type == "date":
            lines.append(f"    {field.name} = Column(Date{', nullable=False' if field.required else ''})")
        elif field.type == "datetime":
            lines.append(f"    {field.name} = Column(DateTime{', nullable=False' if field.required else ''})")
        elif field.type == "enum":
            vals = ", ".join(f'"{v}"' for v in field.enum_values)
            lines.append(f"    {field.name} = Column(Enum({vals}){', nullable=False' if field.required else ''})")
        elif field.type == "uuid" and not field.primary_key:
            lines.append(f"    {field.name} = Column(SA_UUID{', nullable=False' if field.required else ''})")
        if field.relation and field.relation.relation == "many_to_one":
            fk_target = field.relation.target.lower()
            lines.append(f"    {field.name}_id = Column(SA_UUID, ForeignKey('{fk_target}s.id'))")
            lines.append(f"    {field.name} = relationship('{field.relation.target}', foreign_keys=[{field.name}_id])")
    lines.append("")
    return "\n".join(lines)


def generate_schema(model: ModelSchema) -> str:
    lines = [f"from pydantic import BaseModel", "from datetime import date, datetime", "from uuid import UUID", "", ""]
    create_fields = []
    update_fields = []
    for field in model.fields:
        if field.primary_key and field.generated:
            continue
        py_type = _py_type(field)
        if field.required:
            create_fields.append(f"    {field.name}: {py_type}")
            update_fields.append(f"    {field.name}: {py_type} | None = None")
        else:
            create_fields.append(f"    {field.name}: {py_type} | None = None")
            update_fields.append(f"    {field.name}: {py_type} | None = None")

    pk = model.primary_key_field
    pk_type = _py_type(pk) if pk else "str"

    lines.append(f"class {model.name}Base(BaseModel):")
    for f in create_fields:
        lines.append(f)
    lines.append("")
    lines.append(f"class {model.name}Create({model.name}Base):")
    lines.append("    pass")
    lines.append("")
    lines.append(f"class {model.name}Update({model.name}Base):")
    lines.append("    pass")
    lines.append("")
    lines.append(f"class {model.name}Read({model.name}Base):")
    lines.append(f"    id: {pk_type}")
    lines.append("")
    lines.append("    class Config:")
    lines.append("        from_attributes = True")
    lines.append("")
    return "\n".join(lines)


def generate_service(model: ModelSchema) -> str:
    lines = [
        f"from uuid import UUID",
        f"from sqlalchemy.orm import Session",
        f"from app.models.{model.name.lower()} import {model.name}",
        f"from app.schemas.{model.name.lower()} import {model.name}Create, {model.name}Update",
        "",
        "",
        f"class {model.name}Service:",
        f"    def __init__(self, db: Session):",
        f"        self.db = db",
        "",
        f"    def list(self, skip: int = 0, limit: int = 100):",
        f"        return self.db.query({model.name}).offset(skip).limit(limit).all()",
        "",
        f"    def get(self, {model.name.lower()}_id: UUID):",
        f"        return self.db.query({model.name}).filter({model.name}.id == {model.name.lower()}_id).first()",
        "",
        f"    def create(self, payload: {model.name}Create):",
        f"        entity = {model.name}(**payload.model_dump())",
        f"        self.db.add(entity)",
        f"        self.db.commit()",
        f"        self.db.refresh(entity)",
        f"        return entity",
        "",
        f"    def update(self, {model.name.lower()}_id: UUID, payload: {model.name}Update):",
        f"        entity = self.get({model.name.lower()}_id)",
        f"        if not entity:",
        f"            return None",
        f"        for key, value in payload.model_dump(exclude_unset=True).items():",
        f"            setattr(entity, key, value)",
        f"        self.db.commit()",
        f"        self.db.refresh(entity)",
        f"        return entity",
        "",
        f"    def delete(self, {model.name.lower()}_id: UUID):",
        f"        entity = self.get({model.name.lower()}_id)",
        f"        if not entity:",
        f"            return False",
        f"        self.db.delete(entity)",
        f"        self.db.commit()",
        f"        return True",
        "",
    ]
    return "\n".join(lines)


def generate_router(model: ModelSchema) -> str:
    perm = model.permissions
    lines = [
        "from fastapi import APIRouter, Depends, HTTPException",
        "from sqlalchemy.orm import Session",
        f"from app.schemas.{model.name.lower()} import {model.name}Create, {model.name}Update, {model.name}Read",
        f"from app.services.{model.name.lower()} import {model.name}Service",
        "from app.database import get_db",
        "",
        f"router = APIRouter(prefix='/{model.route_path}', tags=['{model.name}'])",
        "",
        f"@router.get('/', response_model=list[{model.name}Read])",
        f"def list_{model.name.lower()}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    return service.list(skip=skip, limit=limit)",
        "",
        f"@router.get('/{{{model.name.lower()}_id}}', response_model={model.name}Read)",
        f"def get_{model.name.lower()}({model.name.lower()}_id: str, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    entity = service.get({model.name.lower()}_id)",
        f"    if not entity:",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        f"    return entity",
        "",
        f"@router.post('/', response_model={model.name}Read, status_code=201)",
        f"def create_{model.name.lower()}(payload: {model.name}Create, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    return service.create(payload)",
        "",
        f"@router.put('/{{{model.name.lower()}_id}}', response_model={model.name}Read)",
        f"def update_{model.name.lower()}({model.name.lower()}_id: str, payload: {model.name}Update, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    entity = service.update({model.name.lower()}_id, payload)",
        f"    if not entity:",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        f"    return entity",
        "",
        f"@router.delete('/{{{model.name.lower()}_id}}', status_code=204)",
        f"def delete_{model.name.lower()}({model.name.lower()}_id: str, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    if not service.delete({model.name.lower()}_id):",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        "",
    ]
    return "\n".join(lines)


def generate_all(app: ApplicationSchema) -> dict[str, str]:
    files: dict[str, str] = {}
    for model in app.models:
        prefix = f"apps/api/src/app/modules/{model.name.lower()}"
        files[f"{prefix}/model.py"] = generate_model(model)
        files[f"{prefix}/schemas.py"] = generate_schema(model)
        files[f"{prefix}/service.py"] = generate_service(model)
        files[f"{prefix}/router.py"] = generate_router(model)
    return files


def _py_type(field: ModelField) -> str:
    mapping = {
        "string": "str",
        "text": "str",
        "integer": "int",
        "float": "float",
        "boolean": "bool",
        "date": "date",
        "datetime": "datetime",
        "enum": "str",
        "uuid": "UUID",
    }
    return mapping.get(field.type, "str")
