from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..core.database import Base

class Local(Base):
    __tablename__ = "locales"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    categoria = Column(String, nullable=True)       # "comida", "farmacia", "supermercado", etc.
    imagen_url = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    activo = Column(Boolean, default=True)
    propietario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)

    propietario = relationship("Usuario", backref="locales")
    productos = relationship("Producto", back_populates="local", cascade="all, delete-orphan")


class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    imagen_url = Column(String, nullable=True)
    disponible = Column(Boolean, default=True)
    local_id = Column(Integer, ForeignKey("locales.id"), nullable=False)

    local = relationship("Local", back_populates="productos")
