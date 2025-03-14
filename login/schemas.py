from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)  # ✅ Updated for Pydantic v2
