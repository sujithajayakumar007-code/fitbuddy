from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .config import settings


Goal = Literal[
    "weight loss",
    "muscle gain",
    "general wellness",
    "flexibility",
]

Intensity = Literal[
    "low",
    "medium",
    "high",
]


class UserInput(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    age: int = Field(
        ge=13,
        le=100,
    )

    weight: float = Field(
        gt=20,
        le=500,
    )

    goal: Goal

    intensity: Intensity

    @field_validator("user_id", "name")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value


class FeedbackRequest(BaseModel):
    user_id: str = Field(
        min_length=1,
        max_length=100,
    )

    feedback: str = Field(
        min_length=3,
        max_length=settings.max_feedback_chars,
    )

    @field_validator("user_id", "feedback")
    @classmethod
    def clean_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("This field cannot be empty.")

        return value