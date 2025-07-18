from pydantic import BaseModel

class JobPayload(BaseModel):
    filename: str
    text: str