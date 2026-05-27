from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: dict

