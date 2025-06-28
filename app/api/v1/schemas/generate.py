from pydantic import BaseModel

class GeneratePostRequest(BaseModel):
    topic: str
    user_id: str