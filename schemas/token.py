from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str
    user_email: str
    user_nivel: str
    user_id: int
    user_nome: str 