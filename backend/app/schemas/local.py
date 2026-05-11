from pydantic import BaseModel
from typing import Optional, List

# --- Producto ---
class ProductoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    imagen_url: Optional[str] = None
    disponible: bool = True

class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None

class ProductoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    precio: float
    imagen_url: Optional[str]
    disponible: bool
    local_id: int

    class Config:
        from_attributes = True

# --- Local ---
class LocalCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None
    direccion: Optional[str] = None

class LocalUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    imagen_url: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

class LocalResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    categoria: Optional[str]
    imagen_url: Optional[str]
    direccion: Optional[str]
    activo: bool
    propietario_id: int

    class Config:
        from_attributes = True

class LocalConProductos(LocalResponse):
    productos: List[ProductoResponse] = []
