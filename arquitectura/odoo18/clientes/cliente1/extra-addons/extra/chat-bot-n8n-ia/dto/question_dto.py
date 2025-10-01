from pydantic import BaseModel, Field
from typing import Optional

class QuestionDto(BaseModel):
    threadId: Optional[str] = Field(None, description="Thread identifier")
    question: Optional[str] = Field(None, description="Pregunta a realizar")