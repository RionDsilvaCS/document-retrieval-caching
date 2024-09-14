from pydantic import BaseModel

class UserBase(BaseModel):
    user_id: str

class User(UserBase):
    id: int
    count: int

    class Config:
        from_attributes = True