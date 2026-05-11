from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ItemPedidoCreate(BaseModel):
    producto_id: int
    cantidad: int

class PedidoCreate(BaseModel):
    local_id: int
    direccion_entrega: str
    items: List[ItemPedidoCreate]

class ItemPedidoResponse(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True

class PedidoResponse(BaseModel):
    id: int
    estado: str
    total: float
    direccion_entrega: str
    created_at: datetime
    cliente_id: int
    local_id: int
    items: List[ItemPedidoResponse] = []

    class Config:
        from_attributes = True

class PedidoEstadoUpdate(BaseModel):
    estado: str  # "en_preparacion", "enviado", "entregado", "cancelado"
