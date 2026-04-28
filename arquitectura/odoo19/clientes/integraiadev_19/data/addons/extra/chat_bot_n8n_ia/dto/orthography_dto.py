from pydantic import BaseModel, Field
from typing import Optional

class OrthographyDto(BaseModel):
    prompt: str = Field(..., description="Texto a verificar")
    max_tokens: Optional[int] = Field(None, description="Número máximo de tokens")