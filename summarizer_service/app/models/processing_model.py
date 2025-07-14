from pydantic import BaseModel

class ProcessingRequest(BaseModel):
    text: str

class ProcessingResponse(BaseModel):
    output: str
