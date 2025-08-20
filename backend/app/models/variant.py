from __future__ import annotations
import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy import Integer, Text, ForeignKey
from .base import Base, IDMixin, TimestampMixin

class LogoVariant(Base, IDMixin, TimestampMixin):
    __tablename__ = "logo_variants"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    palette: Mapped[dict] = mapped_column(JSONB, default=dict)
    svg_key: Mapped[str] = mapped_column(Text, nullable=False)
