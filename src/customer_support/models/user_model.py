from datetime import datetime 
from sqlalchemy import DateTime,String,func
from sqlalchemy.orm import Mapped,mapped_column

from db.base import Base

class User(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(
        primary_key=True,
        index=True
    )

    name:Mapped[str]=mapped_column(
        String(200),
        nullable=False
    )

    email:Mapped[str]=mapped_column(
        String(200),
        nullable=False,
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(
        String(128),
        name="password_hash",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
    )