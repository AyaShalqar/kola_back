from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    refresh_token: str

class LogoutIn(BaseModel):
    refresh_token: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
