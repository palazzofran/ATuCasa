from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Favorito(Base):
    """Local marcado como favorito por un usuario. Un usuario no puede repetir un local."""
    __tablename__ = "favoritos"
    __table_args__ = (UniqueConstraint("usuario_id", "local_id", name="uq_favorito_usuario_local"),)

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True)
    local_id = Column(Integer, ForeignKey("locales.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    local = relationship("Local")
