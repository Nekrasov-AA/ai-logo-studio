import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .base import Base, IDMixin, TimestampMixin

class Job(Base, IDMixin, TimestampMixin):
    __tablename__ = "jobs"
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    business_type: Mapped[str] = mapped_column(String(120))
    prefs: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="queued")
    result_svg_key: Mapped[str | None] = mapped_column(Text, nullable=True)
