from typing import Optional, List
from datetime import datetime

from sqlmodel import SQLModel, Field, Column
from sqlalchemy import Text, JSON


class Resume(SQLModel, table=True):
    __tablename__ = "resumes" # type: ignore

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    fileName: str = Field(
        sa_column=Column(Text, nullable=False)
    )
    
    user_id: int = Field(
        foreign_key="users.id",
        index=True,
        nullable=False
    )

    resume_text: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    overall_score: int

    summary: str = Field(
        sa_column=Column(Text, nullable=False)
    )

    keyword_gaps: List[str] = Field(
        sa_column=Column(JSON, nullable=False)
    )

    formatting_suggestions: List[str] = Field(
        sa_column=Column(JSON, nullable=False)
    )

    actionable_steps: List[str] = Field(
        sa_column=Column(JSON, nullable=False)
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )

    updated_at: datetime = Field(
        default_factory=datetime.utcnow
    )