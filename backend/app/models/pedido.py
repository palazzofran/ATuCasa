from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(
        Enum("pendiente", "en_preparacion", "enviado", "entregado", "cancelado", name="estado_pedido"),
        default="pendiente",
        nullable=False
    )
    total = Column(Float, nullable=False)
    direccion_entrega = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    cliente_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)

    cliente = relationship("Usuario", backref="pedidos")
    local = relationship("Local", backref="pedidos")
    items = relationship("ItemPedido", back_populates="pedido", cascade="all, delete-orphan")


class ItemPedido(Base):
    __tablename__ = "items_pedido"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Float, nullable=False)

    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)

    pedido = relationship("Pedido", back_populates="items")
    producto = relationship("Producto")
