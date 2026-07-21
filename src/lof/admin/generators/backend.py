"""Generates FastAPI backend code from LOF Registry via AdminModel adapter."""

from lof.admin.schema.adapter import AdminApp, AdminModel


def generate_model(model: AdminModel) -> str:
    lines = [
        "from datetime import date, datetime",
        "from uuid import UUID, uuid4",
        'from sqlalchemy import (Column, String, Integer, Float, Boolean,',
        '    Date, DateTime, Enum, Text, ForeignKey)',
        'from sqlalchemy.orm import relationship, declarative_base',
        'from sqlalchemy.dialects.postgresql import UUID as SA_UUID',
        "",
        "Base = declarative_base()",
        "",
    ]
    lines.append(f"class {model.name}(Base):")
    lines.append(f'    __tablename__ = "{model.table_name}"')
    lines.append("")
    for f in model.fields:
        if f.name == "id":
            lines.append(f"    id = Column(SA_UUID, primary_key=True, default=uuid4)")
        elif f.type == "string":
            lines.append(f"    {f.name} = Column(String(255){', nullable=False' if f.required else ''})")
        elif f.type == "text":
            lines.append(f"    {f.name} = Column(Text{', nullable=False' if f.required else ''})")
        elif f.type == "integer":
            lines.append(f"    {f.name} = Column(Integer{', nullable=False' if f.required else ''})")
        elif f.type == "float":
            lines.append(f"    {f.name} = Column(Float{', nullable=False' if f.required else ''})")
        elif f.type == "boolean":
            default = str(f.default).lower() if f.default is not None else "False"
            lines.append(f"    {f.name} = Column(Boolean, default={default})")
        elif f.type == "date":
            lines.append(f"    {f.name} = Column(Date{', nullable=False' if f.required else ''})")
        elif f.type == "datetime":
            lines.append(f"    {f.name} = Column(DateTime{', nullable=False' if f.required else ''})")
        elif f.type == "enum":
            vals = ", ".join(f'"{v}"' for v in f.enum_values)
            lines.append(f"    {f.name} = Column(Enum({vals}){', nullable=False' if f.required else ''})")
    return "\n".join(lines)


def generate_schema(model: AdminModel) -> str:
    lines = [
        "from pydantic import BaseModel",
        "from datetime import date, datetime",
        "from uuid import UUID",
        "",
    ]
    create_lines = []
    update_lines = []
    for f in model.fields:
        if f.name == "id":
            continue
        py_type = f.py_type
        if f.required:
            create_lines.append(f"    {f.name}: {py_type}")
            update_lines.append(f"    {f.name}: {py_type} | None = None")
        else:
            create_lines.append(f"    {f.name}: {py_type} | None = None")

    lines.append(f"class {model.name}Base(BaseModel):")
    for line in create_lines:
        lines.append(line)
    lines.append("")
    lines.append(f"class {model.name}Create({model.name}Base):")
    lines.append("    pass")
    lines.append("")
    lines.append(f"class {model.name}Update({model.name}Base):")
    lines.append("    pass")
    lines.append("")
    lines.append(f"class {model.name}Read({model.name}Base):")
    lines.append("    id: UUID")
    lines.append("")
    lines.append("    class Config:")
    lines.append("        from_attributes = True")
    lines.append("")
    return "\n".join(lines)


def generate_service(model: AdminModel) -> str:
    sn = model.name.lower()
    lines = [
        "from uuid import UUID",
        "from sqlalchemy.orm import Session",
        f"from app.models.{sn} import {model.name}",
        f"from app.schemas.{sn} import {model.name}Create, {model.name}Update",
        "",
        f"class {model.name}Service:",
        f"    def __init__(self, db: Session):",
        f"        self.db = db",
        "",
        f"    def list(self, skip: int = 0, limit: int = 100):",
        f"        return self.db.query({model.name}).offset(skip).limit(limit).all()",
        f"",
        f"    def get(self, {sn}_id: UUID):",
        f"        return self.db.query({model.name}).filter({model.name}.id == {sn}_id).first()",
        f"",
        f"    def create(self, payload: {model.name}Create):",
        f"        entity = {model.name}(**payload.model_dump())",
        f"        self.db.add(entity)",
        f"        self.db.commit()",
        f"        self.db.refresh(entity)",
        f"        return entity",
        f"",
        f"    def update(self, {sn}_id: UUID, payload: {model.name}Update):",
        f"        entity = self.get({sn}_id)",
        "        if not entity:",
        "            return None",
        "        for key, value in payload.model_dump(exclude_unset=True).items():",
        "            setattr(entity, key, value)",
        "        self.db.commit()",
        "        self.db.refresh(entity)",
        "        return entity",
        f"",
        f"    def delete(self, {sn}_id: UUID):",
        f"        entity = self.get({sn}_id)",
        "        if not entity:",
        "            return False",
        "        self.db.delete(entity)",
        "        self.db.commit()",
        "        return True",
        "",
    ]
    return "\n".join(lines)


def generate_router(model: AdminModel) -> str:
    sn = model.name.lower()
    lines = [
        "from fastapi import APIRouter, Depends, HTTPException",
        "from sqlalchemy.orm import Session",
        f"from app.schemas.{sn} import {model.name}Create, {model.name}Update, {model.name}Read",
        f"from app.services.{sn} import {model.name}Service",
        "from app.database import get_db",
        "",
        f"router = APIRouter(prefix='/{model.route_path}', tags=['{model.name}'])",
        "",
        f"@router.get('/', response_model=list[{model.name}Read])",
        f"def list_{sn}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        "    return service.list(skip=skip, limit=limit)",
        "",
        f"@router.get('/{{{sn}_id}}', response_model={model.name}Read)",
        f"def get_{sn}({sn}_id: str, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    entity = service.get({sn}_id)",
        f"    if not entity:",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        "    return entity",
        "",
        f"@router.post('/', response_model={model.name}Read, status_code=201)",
        f"def create_{sn}(payload: {model.name}Create, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        "    return service.create(payload)",
        "",
        f"@router.put('/{{{sn}_id}}', response_model={model.name}Read)",
        f"def update_{sn}({sn}_id: str, payload: {model.name}Update, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    entity = service.update({sn}_id, payload)",
        f"    if not entity:",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        "    return entity",
        "",
        f"@router.delete('/{{{sn}_id}}', status_code=204)",
        f"def delete_{sn}({sn}_id: str, db: Session = Depends(get_db)):",
        f"    service = {model.name}Service(db)",
        f"    if not service.delete({sn}_id):",
        f"        raise HTTPException(status_code=404, detail='{model.name} not found')",
        "",
    ]
    return "\n".join(lines)


def generate_all(app: AdminApp) -> dict[str, str]:
    files = {}
    for model in app.models:
        prefix = f"apps/api/src/app/modules/{model.name.lower()}"
        files[f"{prefix}/model.py"] = generate_model(model)
        files[f"{prefix}/schemas.py"] = generate_schema(model)
        files[f"{prefix}/service.py"] = generate_service(model)
        files[f"{prefix}/router.py"] = generate_router(model)
    return files
