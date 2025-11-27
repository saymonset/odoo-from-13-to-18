from pydantic import BaseModel, Field
from typing import Optional

class TextToAudioDto(BaseModel):
    prompt: str = Field(..., description="Texto a verificar")
    voice: Optional[str] = Field(None, description="Voz para usar en la conversión de texto a audio")