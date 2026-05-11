from sqlalchemy import Column, Integer, String, Enum
from ..core.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    rol = Column(Enum("cliente", "comercio", name="rol_enum"), default="cliente", nullable=False)
