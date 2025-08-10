from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from .base import Base, IDMixin, TimestampMixin

class User(Base, IDMixin, TimestampMixin):
    __tablename__ = "users"
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
