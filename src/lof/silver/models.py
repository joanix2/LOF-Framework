from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ProvenanceRef(BaseModel):
    bronze_id: str | None = None
    span: str | None = None
    silver_id: str | None = None
    explanation: str | None = None


class SilverClaim(BaseModel):
    id: str
    subject: str
    predicate: str
    object: str
    status: Literal["affirmed", "refuted", "candidate", "ambiguous", "hypothetical"] = "candidate"
    confidence: float = 0.5
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class SilverEntity(BaseModel):
    id: str
    name: str
    type: str
    status: Literal["affirmed", "candidate", "hypothetical"] = "candidate"
    attributes: dict[str, Any] = Field(default_factory=dict)
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class SilverRelation(BaseModel):
    id: str
    source: str
    target: str
    kind: str
    status: Literal["affirmed", "refuted", "candidate"] = "candidate"
    confidence: float = 0.5
    cardinality: str | None = None
    inverse: str | None = None
    provenance: list[ProvenanceRef] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class SilverContradiction(BaseModel):
    id: str
    claim_ids: list[str] = Field(default_factory=list)
    description: str
    severity: Literal["info", "warning", "error"] = "warning"
    resolution: str | None = None
    resolved: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
