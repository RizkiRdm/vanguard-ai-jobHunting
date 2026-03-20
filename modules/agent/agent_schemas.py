from pydantic import BaseModel, Field
from typing import List, Optional, Any, Union


class InteractionField(BaseModel):
    id: str = Field(
        ..., description="Unique key for the answer (e.g., 'expected_salary')"
    )
    label: str = Field(..., description="Question text to show the user")
    type: str = Field(..., description="Input type: text, select, boolean, or number")
    options: Optional[List[str]] = None  # Used if type is 'select'
    required: bool = True


class HumanInteractionSchema(BaseModel):
    """The structure AI must follow when requesting human help."""

    fields: List[InteractionField]
    reason: str = Field(..., description="Why the AI is asking this")


class UserAnswerPayload(BaseModel):
    """The structure for user's response to the AI."""

    task_id: str
    answers: dict = Field(
        ..., example={"expected_salary": "5000", "notice_period": "Immediate"}
    )
