from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class InfoWhatsAppDto(BaseModel):
    host_phone: str = Field(..., description="Phone host")
    client_phone: str = Field(..., description="Phone client")
    message_type: str = Field(..., description="type of message")
    instance:     str = Field(..., description="instance text")
    apikey:       str = Field(..., description="apikey text")
    conversation: Optional[str] = Field(None, description="Conversation text")
    base64: Optional[str] = Field(None, description="Base 64 encoded data, if applicable")
    media_url: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of the message")
    
    
    
     