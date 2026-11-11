from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.favorito import Favorito
from ..models.local import Local
from ..models.usuario import Usuario
from ..schemas.local import LocalResponse

router = APIRouter(prefix="/favoritos", tags=["Favoritos"])


@router.get("/", response_model=List[LocalResponse])
def mis_favoritos(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Locales favoritos del usuario autenticado (solo activos), del más reciente al más viejo."""
    return (
        db.query(Local)
        .join(Favorito, Favorito.local_id == Local.id)
        .filter(Favorito.usuario_id == current_user.id, Local.activo == True)
        .order_by(Favorito.created_at.desc())
        .all()
    )


@router.put("/{local_id}", status_code=status.HTTP_204_NO_CONTENT)
def agregar_favorito(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Marca un local como favorito. Es idempotente: si ya era favorito no hace nada."""
    if not db.query(Local).filter(Local.id == local_id, Local.activo == True).first():
        raise HTTPException(status_code=404, detail="Local no encontrado")

    existe = db.query(Favorito).filter_by(usuario_id=current_user.id, local_id=local_id).first()
    if not existe:
        db.add(Favorito(usuario_id=current_user.id, local_id=local_id))
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{local_id}", status_code=status.HTTP_204_NO_CONTENT)
def quitar_favorito(
    local_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Quita un local de favoritos. Es idempotente: si no era favorito no hace nada."""
    db.query(Favorito).filter_by(usuario_id=current_user.id, local_id=local_id).delete()
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
