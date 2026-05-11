from pydantic import BaseModel, EmailStr
from typing import Literal

class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telefono: str | None = None
    rol: Literal["cliente", "comercio"] = "cliente"

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: str | None
    rol: str

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioResponse
