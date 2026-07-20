from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BronzeAttachment(BaseModel):
    type: str
    url: str | None = None
    content: str | None = None
    mime_type: str | None = None


class BronzeConversationRef(BaseModel):
    conversation_id: str
    parent_entry_id: str | None = None


class BronzeEntry(BaseModel):
    id: str
    created_at: datetime
    source: str = "user"
    author: str = "user"
    content: str
    attachments: list[BronzeAttachment] = Field(default_factory=list)
    conversation_id: str | None = None
    parent_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    entry_type: str = "message"


class BronzeEvent(BaseModel):
    id: str
    timestamp: datetime
    event_type: str
    entry_id: str
    payload: dict[str, Any] = Field(default_factory=dict)
